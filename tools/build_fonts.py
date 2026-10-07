"""Subset bundled M+ glyphs; make a 2x pixel title font without smoothing."""
from pathlib import Path
import re
import pyxel
root = Path(__file__).resolve().parents[1]
chars=set(''.join(p.read_text() for p in (root/'game').glob('*.py')))
chars.update(map(chr,range(32,127)))
chars.update('…２１＋／－→０３４５６７８９')
source=(Path(pyxel.__file__).parent/'examples/assets/umplus_j12r.bdf').read_text()
blocks=re.findall(r'STARTCHAR .*?ENDCHAR',source,re.S)
# Later ASCII definitions override earlier ones, matching the source's combined fonts.
by_code={}
for b in blocks:
 m=re.search(r'ENCODING (-?\d+)',b)
 if m and int(m[1])>=0 and chr(int(m[1])) in chars: by_code[int(m[1])]=b
missing=[c for c in chars if not c.isspace() and ord(c)>127 and ord(c) not in by_code]
if missing: raise ValueError('Missing glyphs: '+''.join(missing))
header=source.split('CHARS ')[0]
(root/'game/assets/japanese.bdf').write_text(header+f'CHARS {len(by_code)}\n'+'\n'.join(by_code.values())+'\nENDFONT\n')
titlechars=set('冥界執行局追加の印章を選ぶ官0123456789 点')
scaled=[]
for code,b in by_code.items():
 if chr(code) not in titlechars: continue
 b=re.sub(r'(DWIDTH|BBX) ([^\n]+)',lambda m:m[1]+' '+' '.join(str(int(v)*2) for v in m[2].split()),b)
 rows=b.split('BITMAP\n')[1].split('\nENDCHAR')[0].splitlines()
 bitmap=[]
 # BDF rows are high-bit aligned; duplicate every input bit and every scanline.
 for row in rows:
  bits=bin(int(row,16))[2:].zfill(len(row)*4)
  doubled=''.join(bit*2 for bit in bits)
  out=f'{int(doubled,2):0{len(doubled)//4}X}'
  bitmap.extend([out,out])
 b=b.split('BITMAP\n')[0]+'BITMAP\n'+'\n'.join(bitmap)+'\nENDCHAR'
 scaled.append(b)
head='STARTFONT 2.1\nFONT -underworld-title-24\nSIZE 24 75 75\nFONTBOUNDINGBOX 24 28 0 -4\nSTARTPROPERTIES 2\nFONT_ASCENT 24\nFONT_DESCENT 4\nENDPROPERTIES\n'
(root/'game/assets/title.bdf').write_text(head+f'CHARS {len(scaled)}\n'+'\n'.join(scaled)+'\nENDFONT\n')
print('Glyphs:',len(by_code),'title:',len(scaled))
