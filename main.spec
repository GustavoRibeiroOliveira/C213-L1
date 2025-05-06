a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('app/templates/home.html', 'templates'),
        ('app/static/css/home.css', 'static/css'),
        ('app/static/js/home.js', 'static/js'),
        ('app/static/js/axios/axios.min.js', 'static/js/axios'),
        ('app/static/js/jquery/jquery.min.js', 'static/js/jquery'),
        ('app/Dataset_Grupo1.mat', 'app')
    ],
    hiddenimports=[
        'engineio',
        'threading',
        'engineio.async_drivers',
        'engineio.async_drivers.threading',
        'engineio.async_server',
        'engineio.async_socket'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='Projeto Prático C213 - Sistemas Embarcados',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    uac_admin=True,
)