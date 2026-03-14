"""Demo of the embroidery drawing library."""

from drawing import Canvas

c = Canvas(stitch_length=2.5)

# Unfilled square (original requirement)
c.rectangle(10, 10, 50, 50)

# Some additional shapes to demonstrate the library
c.circle(100, 35, 25)
c.ellipse(170, 35, 30, 20)
c.star(240, 35, 25, 10)
c.rounded_rectangle(10, 80, 50, 40, 8)

# A filled shape
c.color("red")
c.filled_circle(100, 100, 20, angle=45)

# A bezier curve
c.color("blue")
c.curve((140, 80), (160, 60), (180, 120), (200, 80))

# Satin-stitched line
c.color("green")
c.satin_line(10, 140, 80, 140, width=4)

# Text
c.color("black")
c.text(10, 160, "Hello!", size=12)

c.save("demo.dst")
print("Created demo.dst")

# Also save the simple square on its own
sq = Canvas()
sq.rectangle(10, 10, 50, 50)
sq.save("square.dst")
print("Created square.dst")
