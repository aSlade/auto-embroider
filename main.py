import pyembroidery

pattern = pyembroidery.EmbPattern()

# Unfilled square: 100mm x 100mm starting at (10mm, 10mm)
# pyembroidery uses 0.1mm units
x0, y0 = 100, 100  # 10mm, 10mm
size = 1000         # 100mm

pattern.add_command(pyembroidery.STITCH, x0, y0)
pattern.add_command(pyembroidery.STITCH, x0 + size, y0)
pattern.add_command(pyembroidery.STITCH, x0 + size, y0 + size)
pattern.add_command(pyembroidery.STITCH, x0, y0 + size)
pattern.add_command(pyembroidery.STITCH, x0, y0)
pattern.add_command(pyembroidery.END)

pyembroidery.write_dst(pattern, "square.dst")
print("Created square.dst")
