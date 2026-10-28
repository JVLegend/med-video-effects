"""Testes de comportamento e integração com mídia real. #Tecnologia #Saude"""
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from PIL import Image
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
import effects

ROOT = Path(__file__).resolve().parent.parent
CLI = [sys.executable, str(ROOT / 'scripts/effects.py')]


def run(args, ok=True):
    r = subprocess.run(args, capture_output=True, text=True)
    if ok and r.returncode:
        raise AssertionError(r.stdout + r.stderr)
    return r


def probe(path):
    return json.loads(run(['ffprobe', '-v', 'error', '-show_streams', '-show_format', '-of', 'json', str(path)]).stdout)


def audiohash(path):
    raw = subprocess.check_output(['ffmpeg','-v','error','-i',str(path),'-map','0:a:0','-c:a','copy','-f','adts','-'])
    return hashlib.sha256(raw).hexdigest()


class MediaIntegration(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temporary = tempfile.TemporaryDirectory(prefix='medfx-test-')
        cls.dir = Path(cls.temporary.name)
        cls.source = cls.dir / 'video com espaços.mp4'
        run(['ffmpeg','-v','error','-loop','1','-i',str(ROOT/'assets/example-frame.jpg'),'-f','lavfi','-i','sine=frequency=440:duration=3:sample_rate=44100','-vf','scale=240:426','-t','3','-r','30','-c:v','libx264','-preset','ultrafast','-pix_fmt','yuv420p','-c:a','aac',str(cls.source)])
        cls.original_hash = hashlib.sha256(cls.source.read_bytes()).hexdigest()

    @classmethod
    def tearDownClass(cls):
        cls.temporary.cleanup()

    def tearDown(self):
        self.assertEqual(self.original_hash, hashlib.sha256(self.source.read_bytes()).hexdigest())

    def test_forty_five_effects_export_and_keep_audio(self):
        names = list(effects.EFFECTS)
        self.assertEqual(len(names),45)
        step=3/len(names)
        plan = {'effects':[{'effect':name,'start':i*step,'end':(i+1)*step} for i,name in enumerate(names)]}
        f=self.dir/'plano.json';f.write_text(json.dumps(plan))
        out=self.dir/'todos.mp4'
        run(CLI+['render',str(self.source),str(out),'--plan',str(f),'--width','240'])
        info=probe(out)
        self.assertEqual((info['streams'][0]['width'], info['streams'][0]['height']), (240,426))
        self.assertAlmostEqual(float(info['format']['duration']),3,delta=.06)
        self.assertEqual(audiohash(self.source),audiohash(out))
        run(['ffmpeg','-v','error','-i',str(out),'-f','null','-'])

    def test_new_effects_are_visible_and_animate(self):
        frame=np.array(Image.open(ROOT/'assets/example-frame.jpg').convert('RGB'))
        face=effects.FaceTracker().update(frame)
        self.assertIsNotNone(face)
        for name in sorted(effects.full_effects.FULL_NAMES | set(effects.EFFECTS)):
            with self.subTest(effect=name):
                e=effects.validate_plan([{'effect':name,'start':0,'end':4}],4)[0]
                first,_=effects.render_effect(frame.copy(),face.copy(),e,.1)
                later,_=effects.render_effect(frame.copy(),face.copy(),e,2.7)
                self.assertEqual(first.shape,frame.shape)
                self.assertEqual(later.dtype,np.uint8)
                self.assertGreater(float(np.abs(first.astype(float)-later.astype(float)).mean()),.001)
                if name=='dot-reveal':
                    self.assertTrue(np.array_equal(later,frame))
                elif name not in ('pause-point','swipe','slow-push'):
                    self.assertFalse(np.array_equal(later,frame))

    def test_new_effects_handle_missing_face(self):
        frame=np.zeros((426,240,3),dtype=np.uint8)
        for name in sorted(effects.full_effects.FULL_NAMES | set(effects.EFFECTS)):
            with self.subTest(effect=name):
                e=effects.validate_plan([{'effect':name,'start':0,'end':4}],4)[0]
                out,face=effects.render_effect(frame.copy(),None,e,1.5)
                self.assertEqual(out.shape,frame.shape)
                self.assertIsNone(face)
                if name=='lean-in':
                    self.assertTrue(np.array_equal(out,frame))

    def test_text_limits_for_new_cards(self):
        invalid=[{'effect':'stamp','text':'A'*33},
                 {'effect':'lineup','text':'um|dois|três|quatro'},
                 {'effect':'comment','text':'uma|duas'}]
        for raw in invalid:
            with self.subTest(raw=raw),self.assertRaises(ValueError):
                effects.validate_plan([dict(raw,start=0,end=3)],3)

    def test_friendly_names_and_previous_names_remain_usable(self):
        pairs={'Órbita':'orbit','Título em caixa':'headline-box','focus':'locked-on',
               'grade':'moody','receipt':'the-bill','glass':'glass-widgets'}
        for label,canonical in pairs.items():
            with self.subTest(label=label):
                e=effects.validate_plan([dict(effect=label,start=0,end=2)],2)[0]
                self.assertEqual(e['effect'],canonical)
        out=self.dir/'portugues.png'
        run(CLI+['preview',str(self.source),str(out),'--effect','Título em caixa','--at','1','--width','240'])
        self.assertTrue(out.is_file())

    def test_cards_use_only_supplied_local_images(self):
        folder=self.dir/'minhas imagens';folder.mkdir()
        Image.new('RGB',(100,100),(255,0,0)).save(folder/'vermelho.png')
        e=effects.validate_plan([dict(effect='orbit',images=str(folder),start=0,end=2)],2)[0]
        frame=np.zeros((426,240,3),dtype=np.uint8)
        out,_=effects.render_effect(frame,None,e,1)
        red=(out[:,:,0]>200)&(out[:,:,1]<60)&(out[:,:,2]<60)
        self.assertGreater(int(red.sum()),100)
        self.assertEqual(len(e['_cards']),1)

    def test_pause_reuses_the_initial_frame(self):
        e=effects.validate_plan([dict(effect='pause-point',start=0,end=3)],3)[0]
        start=np.full((426,240,3),(20,70,100),dtype=np.uint8)
        changed=np.full((426,240,3),(200,10,20),dtype=np.uint8)
        effects.render_effect(start,None,e,.1)
        out,_=effects.render_effect(changed,None,e,1.5)
        self.assertTrue(np.array_equal(out[250:400],start[250:400]))

    def test_preview_writes_a_real_png(self):
        out=self.dir/'previa.png'
        run(CLI+['preview',str(self.source),str(out),'--effect','headline','--text','Informação clara|Saúde','--end','3','--at','1','--width','240'])
        with Image.open(out) as im:
            self.assertEqual(im.format,'PNG');self.assertEqual(im.size,(240,426))

    def test_output_and_original_cannot_be_overwritten(self):
        out=self.dir/'sentinela.mp4';out.write_bytes(b'preservar')
        r=run(CLI+['render',str(self.source),str(out),'--effect','grade'],ok=False)
        self.assertNotEqual(r.returncode,0);self.assertEqual(out.read_bytes(),b'preservar')
        r=run(CLI+['render',str(self.source),str(self.source),'--effect','grade'],ok=False)
        self.assertNotEqual(r.returncode,0)

    def test_overlapping_or_invalid_intervals_leave_no_output(self):
        cases=[
            [{'effect':'headline','start':0,'end':2},{'effect':'focus','start':1,'end':3}],
            [{'effect':'focus','start':2,'end':1}],
            [{'effect':'focus','start':float('nan'),'end':1}],
        ]
        for i,items in enumerate(cases):
            f=self.dir/f'invalido{i}.json';f.write_text(json.dumps({'effects':items}))
            out=self.dir/f'invalido{i}.mp4'
            r=run(CLI+['render',str(self.source),str(out),'--plan',str(f)],ok=False)
            self.assertNotEqual(r.returncode,0);self.assertFalse(out.exists())

    def test_video_without_audio_stays_silent(self):
        silent=self.dir/'silencioso.mp4';out=self.dir/'silencioso-editado.mp4'
        run(['ffmpeg','-v','error','-i',str(self.source),'-an','-c:v','copy',str(silent)])
        run(CLI+['render',str(silent),str(out),'--effect','grade','--end','1','--width','240'])
        self.assertEqual([s['codec_type'] for s in probe(out)['streams']],['video'])

    def test_display_rotation_is_applied(self):
        rotated=self.dir/'rotacao.mp4';out=self.dir/'rotacao.png'
        run(['ffmpeg','-v','error','-display_rotation:v:0','90','-i',str(self.source),'-c','copy',str(rotated)])
        self.assertEqual(probe(rotated)['streams'][0]['side_data_list'][0]['rotation'],90)
        run(CLI+['preview',str(rotated),str(out),'--effect','grade','--at','1','--width','320'])
        with Image.open(out) as im:self.assertEqual(im.size,(320,180))

    def test_hdr_is_rejected_before_export(self):
        hdr=self.dir/'hdr.mp4';out=self.dir/'hdr-editado.mp4'
        run(['ffmpeg','-v','error','-i',str(self.source),'-an','-c:v','copy','-bsf:v','h264_metadata=transfer_characteristics=16:colour_primaries=9:matrix_coefficients=9',str(hdr)])
        self.assertEqual(probe(hdr)['streams'][0]['color_transfer'],'smpte2084')
        r=run(CLI+['render',str(hdr),str(out),'--effect','grade'],ok=False)
        self.assertNotEqual(r.returncode,0);self.assertIn('HDR',r.stderr);self.assertFalse(out.exists())


if __name__=='__main__':unittest.main()
