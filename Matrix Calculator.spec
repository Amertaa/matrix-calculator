# -*- mode: python ; coding: utf-8 -*-
from kivy_deps import sdl2, glew
from kivymd import hooks_path as kivymd_hooks_path
block_cipher = None


a = Analysis(['Desktop\\main.py'],
             pathex=['D:\\Softwares\\Android'],
             binaries=[],
             datas=[('matrixcalculator.kv','.'),('assets\\','assets')],
             hiddenimports=[],
             hookspath=[kivymd_hooks_path],
             runtime_hooks=[],
             excludes=['numpy', 'docutils', 'pygments', 'PIL'],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
	  *[Tree(p) for p in (sdl2.dep_bins + glew.dep_bins)],
          [],
          name='Matrix Calculator ITK',
          debug=False,
          bootloader_ignore_signals=False,
          strip=True,
          upx=True,
          upx_exclude=[],
          runtime_tmpdir=None,
          console=False)
