"""
Create professional beetle architecture diagram to replace ASCII art
"""

import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch, Ellipse, Rectangle, Polygon
import numpy as np

# Set up the figure with modern style
plt.style.use('seaborn-v0_8-darkgrid')
fig = plt.figure(figsize=(14, 10))

# Define consistent color scheme
colors = {
    'solar': '#FFD700',      # Gold
    'lattice': '#4A90E2',    # Blue
    'bio': '#7ED321',        # Green
    'processor': '#F5515F',   # Red
    'structure': '#9013FE',   # Purple
    'text': '#2C3E50'        # Dark blue-gray
}

# Create two subplots - top view and side view
ax1 = plt.subplot(2, 1, 1)
ax2 = plt.subplot(2, 1, 2)

# TOP VIEW
ax1.set_xlim(0, 10)
ax1.set_ylim(0, 8)
ax1.set_aspect('equal')
ax1.axis('off')
ax1.set_title('TOP VIEW - Integrated System Architecture', fontsize=14, fontweight='bold', color=colors['text'])

# Main body outline (beetle shape)
beetle_body = Ellipse((5, 4), 6, 4, facecolor='none', edgecolor=colors['text'], linewidth=2)
ax1.add_patch(beetle_body)

# Solar carapace
solar_patch = Ellipse((5, 4), 5.5, 3.5, facecolor=colors['solar'], alpha=0.3, edgecolor=colors['solar'], linewidth=2)
ax1.add_patch(solar_patch)
ax1.text(5, 6, 'Solar Carapace\n1500 cm²\n20% efficiency', ha='center', va='center', fontsize=10, fontweight='bold')

# Flow lattice core
lattice_rect = FancyBboxPatch((2.5, 2.5), 5, 3, boxstyle="round,pad=0.1", 
                              facecolor=colors['lattice'], alpha=0.3, edgecolor=colors['lattice'], linewidth=2)
ax1.add_patch(lattice_rect)

# Hexagonal pattern inside lattice
for i in range(3, 8):
    for j in range(2, 6):
        if (i + j) % 2 == 0:
            hex_x = i * 0.6
            hex_y = j * 0.6
            hexagon = patches.RegularPolygon((hex_x, hex_y), 6, radius=0.2, 
                                            facecolor='none', edgecolor=colors['lattice'], linewidth=0.5)
            ax1.add_patch(hexagon)

ax1.text(5, 4, 'Multi-Functional\nFlow Lattice\n>1000 micro-chambers\n70% porosity', 
         ha='center', va='center', fontsize=9, style='italic')

# Bio-reactors (distributed)
for x, y in [(3, 3), (7, 3), (3.5, 5), (6.5, 5)]:
    bio = plt.Circle((x, y), 0.3, facecolor=colors['bio'], alpha=0.5, edgecolor=colors['bio'], linewidth=1)
    ax1.add_patch(bio)

ax1.text(2, 2.5, 'Bio-reactors\n2-5L total', ha='center', fontsize=8, color=colors['bio'])

# Processor location
processor = Rectangle((4.5, 3.5), 1, 1, facecolor=colors['processor'], alpha=0.5, edgecolor=colors['processor'], linewidth=2)
ax1.add_patch(processor)
ax1.text(5, 3, 'Snapdragon\n5-15W', ha='center', fontsize=8, color=colors['processor'], fontweight='bold')

# Six legs (beetle-style)
leg_positions = [(1.5, 5), (1.5, 3), (1.5, 1), (8.5, 5), (8.5, 3), (8.5, 1)]
for x, y in leg_positions:
    ax1.plot([5, x], [4, y], 'k-', linewidth=2, alpha=0.7)
    ax1.plot(x, y, 'ko', markersize=8)

ax1.text(1, 0.5, '6 × Nitinol\nActuated Legs', ha='center', fontsize=8, color=colors['structure'])

# Component labels with lines
ax1.annotate('Tesla/Vortex Valves', xy=(6, 4.5), xytext=(8.5, 6.5),
            arrowprops=dict(arrowstyle='->', color=colors['text'], alpha=0.5),
            fontsize=8, color=colors['text'])

ax1.annotate('Acoustic Resonators', xy=(4, 4.5), xytext=(1.5, 6.5),
            arrowprops=dict(arrowstyle='->', color=colors['text'], alpha=0.5),
            fontsize=8, color=colors['text'])

# SIDE VIEW
ax2.set_xlim(0, 10)
ax2.set_ylim(0, 6)
ax2.set_aspect('equal')
ax2.axis('off')
ax2.set_title('SIDE VIEW - Beetle Profile (25cm height)', fontsize=14, fontweight='bold', color=colors['text'])

# Beetle side profile (more realistic)
# Body
body_points = np.array([
    [2, 2], [2, 3.5], [3, 4.5], [5, 5], [7, 4.5], [8, 3.5], [8, 2]
])
body_polygon = Polygon(body_points, closed=True, facecolor='lightgray', edgecolor=colors['text'], linewidth=2)
ax2.add_patch(body_polygon)

# Solar carapace (top curve)
carapace_x = np.linspace(2, 8, 100)
carapace_y = 4.5 - 0.5 * ((carapace_x - 5) / 3) ** 2
ax2.fill_between(carapace_x, carapace_y, 5, alpha=0.3, color=colors['solar'], edgecolor=colors['solar'], linewidth=2)
ax2.text(5, 4.7, 'Solar Carapace', ha='center', fontsize=10, fontweight='bold', color=colors['solar'])

# Flow lattice layer
ax2.fill_between([2.5, 7.5], [2.5, 2.5], [4, 4], alpha=0.3, color=colors['lattice'])
ax2.text(5, 3.2, 'Flow Lattice Core', ha='center', fontsize=10, color=colors['lattice'], fontweight='bold')

# Bio-reactors layer
ax2.fill_between([3, 7], [2.2, 2.2], [2.8, 2.8], alpha=0.5, color=colors['bio'])
ax2.text(5, 2.5, 'Bio-reactors', ha='center', fontsize=9, color=colors['bio'])

# Legs
leg_x = [2.5, 4, 5, 6, 7.5]
for x in leg_x:
    # Upper segment
    ax2.plot([x, x-0.3], [2, 1], 'k-', linewidth=3)
    # Lower segment  
    ax2.plot([x-0.3, x-0.5], [1, 0.2], 'k-', linewidth=3)
    # Joint
    ax2.plot(x-0.3, 1, 'ko', markersize=6)

ax2.text(5, 0.5, '6 Articulated Legs\nCarbon Fiber + Nitinol', ha='center', fontsize=9, color=colors['structure'])

# Dimensions
ax2.annotate('', xy=(8.5, 2), xytext=(8.5, 5),
            arrowprops=dict(arrowstyle='<->', color='gray', lw=1))
ax2.text(8.8, 3.5, '25 cm', rotation=90, va='center', fontsize=9, color='gray')

ax2.annotate('', xy=(2, 1.5), xytext=(8, 1.5),
            arrowprops=dict(arrowstyle='<->', color='gray', lw=1))
ax2.text(5, 1.2, '50 cm', ha='center', fontsize=9, color='gray')

# Mass indicator
ax2.text(1, 3, '8-15 kg\ntotal mass', ha='center', fontsize=9, 
         bbox=dict(boxstyle="round,pad=0.3", facecolor='white', edgecolor='gray'))

plt.tight_layout()
plt.savefig('C:/Users/Jay/My Drive/ROBOTICS/TB/paper/figures/beetle_architecture.png', dpi=300, bbox_inches='tight')
plt.savefig('C:/Users/Jay/My Drive/ROBOTICS/TB/paper/figures/beetle_architecture.pdf', bbox_inches='tight')
print("Beetle architecture diagram created successfully!")
plt.show()