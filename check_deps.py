import sys, os, glob
print("python", sys.version.split()[0])
try:
    import PIL; print("Pillow", PIL.__version__)
except Exception as e:
    print("Pillow MISSING", e)
try:
    import numpy; print("numpy", numpy.__version__)
except Exception as e:
    print("numpy MISSING", e)

cands = []
for pat in ["msyh*.tt*", "msyhbd*.tt*", "simhei*", "simsun*", "Deng*.tt*", "SourceHan*", "NotoSansSC*", "NotoSerifSC*"]:
    cands += glob.glob(os.path.join(r"C:\Windows\Fonts", pat))
print("FONTS:", sorted(set(cands)))
