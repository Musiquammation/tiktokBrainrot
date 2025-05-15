from screen import *
import pygame
import math
import random

PARTICLE_GRAVITY = .3
SPACING = 15
ANGLE_INCREMENT = 10
ARC_WIDTH = 5
ARC_LENGTH = math.pi * 1.5

BOOST_PER_RADIUS = .005
MAX_SPEED = 8
MIN_SPEED = 5

# Bézier easing
def cubic_bezier(t, p0, p1, p2, p3):
	return (1 - t)**3 * p0 + 3 * (1 - t)**2 * t * p1 + 3 * (1 - t) * t**2 * p2 + t**3 * p3

def cubic_bezier_ease(t, x1, y1, x2, y2):
	t2 = t * t
	t3 = t2 * t
	return (1 - t)**3 * 0 + 3 * (1 - t)**2 * t * x1 + 3 * (1 - t) * t2 * x2 + t3

# Couleur bleu -> rose
def gradient(param):
	if int(param) % 2 == 0:
		param = param%1
	elif param == int(param):
		param = 1
	else:
		param = (1-param)%1

	param = max(0, min(1, param))
	start_color = (0, 0, 255)
	end_color = (255, 105, 180)
	r = int(start_color[0] + (end_color[0] - start_color[0]) * param)
	g = int(start_color[1] + (end_color[1] - start_color[1]) * param)
	b = int(start_color[2] + (end_color[2] - start_color[2]) * param)
	return (r, g, b)

# Collision cercle / arc
def collision_ball_arc(bx, by, r_ball, R_arc, theta_start, theta_end):
	dx = bx - WIDTH/2
	dy = by - HEIGHT/2
	d = math.sqrt(dx*dx + dy*dy)
	if d - r_ball > R_arc or d + r_ball < R_arc + ARC_WIDTH:
		return 0

	angle = math.atan2(-dy, dx)
	if angle < 0:
		angle += 2*math.pi

	theta_start %= (2*math.pi)
	theta_end %= (2*math.pi)

	if theta_start <= theta_end:
		if theta_start <= angle <= theta_end:
			return 1
	else:
		if angle >= theta_start or angle <= theta_end:
			return 1

	return -1


def draw_text_with_stroke(surface, text, font, pos, stroke_color, fill_color=(255, 255, 255)):
	# Texte principal en blanc (remplissage)
	text_surface = font.render(text, True, fill_color)

	# Texte pour contour
	stroke_surface = font.render(text, True, stroke_color)

	x, y = pos

	# Créer le contour en dessinant autour du texte central
	for dx in [-2, -1, 0, 1, 2]:
		for dy in [-2, -1, 0, 1, 2]:
			if dx != 0 or dy != 0:
				surface.blit(stroke_surface, (x + dx, y + dy))

	# Texte blanc par-dessus (remplissage)
	surface.blit(text_surface, (x, y))





# Arc animé
class Arc:
	index = 0

	def __init__(self, radius: float, angle: float):
		self.radius = radius
		self.angle = angle
		self.target_radius = radius
		self.color = gradient(Arc.index / 25)
		self.animation_progress = 1.0
		self.is_animating = False
		Arc.index += 1

	def update(self):
		if self.is_animating:
			self.animation_progress += 0.001
			if self.animation_progress >= 1.0:
				self.animation_progress = 1.0
				self.is_animating = False

			eased_progress = cubic_bezier_ease(self.animation_progress, 0.25, 0.1, 0.25, 1)
			self.radius = self.radius + eased_progress * (self.target_radius - self.radius)

# Particules
class Particle:
	def __init__(self, x, y, color):
		self.x = x
		self.y = y
		self.vx = random.uniform(-1, 1)
		self.vy = random.uniform(-1, 1)
		self.radius = random.uniform(2, 5)
		self.life = random.uniform(.1, .4)
		self.color = color

	def update(self, dt):
		self.vy += PARTICLE_GRAVITY * dt
		self.x += self.vx * dt * 60
		self.y += self.vy * dt * 60
		self.life -= dt

	def draw(self, screen):
		if self.life > 0:
			alpha = max(0, int(255 * (self.life / .4)))
			surf = pygame.Surface((self.radius*2, self.radius*2), pygame.SRCALPHA)
			pygame.draw.circle(surf, (*self.color, alpha), (self.radius, self.radius), self.radius)
			screen.blit(surf, (self.x - self.radius, self.y - self.radius))

# Balle
class Ball:
	def __init__(self):
		self.x = WIDTH / 2
		self.y = HEIGHT / 2
		self.vx = -1
		self.vy = 0
		self.size = 10
		self.last: Arc = None

# Jeu principal
class Game:
	def __init__(self):
		self.frame = 0
		self.ball = Ball()
		self.arcs = [Arc(i * SPACING, 3*math.pi/4) for i in range(5, 40)]
		self.particles = []


		self.dumb_yes = 0
		self.dumb_no = 0
		self.dumb_y = HEIGHT/2
		self.font = pygame.font.SysFont(None, 64)


	def run(self):
		if self.frame % 20 == 0:
			self.dumb_y += 1

		self.ball.vy += PARTICLE_GRAVITY
		self.ball.x += self.ball.vx
		self.ball.y += self.ball.vy

		for arc in self.arcs:
			arc.angle += (arc.radius - 3*SPACING) / 30000
			arc.update()

		result = self.check_collisions()

		# Update particles
		dt = 1 / 60
		self.particles = [p for p in self.particles if p.life > 0]
		for p in self.particles:
			p.update(dt)


		# return self.frame % 15 == 0
		return result


	def check_collisions(self):
		dx = self.ball.x - WIDTH / 2
		dy = self.ball.y - HEIGHT / 2
		distance = math.hypot(dx, dy)
		angle = math.atan2(dy, dx)
		if angle < 0:
			angle += 2 * math.pi


		result = False

		for i, arc in enumerate(self.arcs):
			

			collResult = collision_ball_arc(self.ball.x, self.ball.y, self.ball.size, arc.radius, arc.angle, arc.angle + ARC_LENGTH)

			if collResult == 1:
				nx = dx / distance
				ny = dy / distance
				dot = self.ball.vx * nx + self.ball.vy * ny
				self.ball.vx -= 2 * dot * nx
				self.ball.vy -= 2 * dot * ny

				if self.ball.last != arc:
					self.ball.last = arc
					boost = 1 + 1
					self.ball.vx *= boost
					self.ball.vy *= boost
					norm = self.ball.vx * self.ball.vx + self.ball.vy * self.ball.vy
					if norm > MAX_SPEED * MAX_SPEED:
						norm = MAX_SPEED / math.sqrt(norm)
						self.ball.vx *= norm
						self.ball.vy *= norm
					elif norm < MIN_SPEED*MIN_SPEED:
						norm = MIN_SPEED / math.sqrt(norm)
						self.ball.vx *= norm
						self.ball.vy *= norm

				correct_distance = arc.radius + (self.ball.size * (1 if distance - arc.radius > 0 else -1))
				self.ball.x = WIDTH / 2 + nx * correct_distance
				self.ball.y = HEIGHT / 2 + ny * correct_distance
				
				if self.ball.y <= self.dumb_y:
					self.dumb_no += 1
				else:
					self.dumb_yes += 1

				result = True

			if collResult == 1 or collResult == -1:
				# Effet de particules sur tout l'arc
				arc_color = arc.color
				
				# Calcul des particules le long de l'arc
				num_particles = int(arc.radius)  # Nombre de particules à générer sur l'arc
				for j in range(num_particles):
					# Calculer l'angle de chaque particule
					t = j / (num_particles - 1)
					angle_on_arc = arc.angle + t * ARC_LENGTH
					px = WIDTH / 2 + math.cos(angle_on_arc) * arc.radius
					py = HEIGHT / 2 + math.sin(angle_on_arc) * arc.radius
					self.particles.append(Particle(px, py, arc_color))

				# Supprimer et réajuster les arcs
				self.arcs = self.arcs[(i + 1):]
				length = len(self.arcs)
				angle = self.arcs[length-1].angle


				for j in range(i+1):
					self.arcs.append(Arc(
						self.arcs[length + j - 1].target_radius + SPACING,
						angle
					))

				for j in self.arcs:
					j.target_radius -= SPACING * (i + 1)
					j.is_animating = True
					j.animation_progress = 0

				break

		return result
	

	def draw(self, screen: pygame.Surface):
		# Background
		screen.fill((0, 0, 0))

		dumb_y = int(self.dumb_y)

		pygame.draw.rect(screen, (0, 15, 0), (0, 0, WIDTH, dumb_y))
		pygame.draw.rect(screen, (15, 0, 0), (0, dumb_y, WIDTH, dumb_y))

		# Draw arcs
		for i, arc in enumerate(self.arcs):
			radius = arc.radius
			start_angle = arc.angle
			end_angle = start_angle + ARC_LENGTH
			rect = pygame.Rect(WIDTH / 2 - radius, HEIGHT / 2 - radius, radius * 2, radius * 2)
			pygame.draw.arc(screen, arc.color, rect, start_angle, end_angle, ARC_WIDTH)

		# Draw ball
		pygame.draw.circle(screen, (200, 100, 255), (int(self.ball.x), int(self.ball.y)), self.ball.size)

		# Draw particles
		for p in self.particles:
			p.draw(screen)
		


		
		# Ligne horizontale au centre
		pygame.draw.line(screen, (255, 255, 255), (0, dumb_y), (WIDTH, dumb_y), 2)

		# ====== TITRE PRINCIPAL ======
		title_text = "WILL YOU BE DUMB?"
		title_y = HEIGHT // 4  # position verticale proche du centre
		txt_title = self.font.render(title_text, True, (255, 255, 255))
		title_x = WIDTH // 2 - txt_title.get_width() // 2

		# Dessiner le titre avec contour noir
		draw_text_with_stroke(screen, title_text, self.font, (title_x, title_y), stroke_color=gradient(self.frame/60))

		# ====== YES / NO SCORES ======
		yes_text = f"YES: {self.dumb_yes}"
		no_text = f"NO: {self.dumb_no}"

		# Calcul des surfaces pour la taille
		yes_surface = self.font.render(yes_text, True, (255, 255, 255))
		no_surface = self.font.render(no_text, True, (255, 255, 255))

		# Calcul de la position pour centrer YES et NO côte à côte
		spacing = 40  # espace entre YES et NO
		total_width = yes_surface.get_width() + no_surface.get_width() + spacing
		start_x = WIDTH // 2 - total_width // 2

		scores_y = title_y + txt_title.get_height() + 20  # juste sous le titre

		# Dessiner YES avec contour rouge
		draw_text_with_stroke(screen, yes_text, self.font, (start_x, scores_y), stroke_color=(255, 0, 0))

		# Dessiner NO avec contour vert
		no_x = start_x + yes_surface.get_width() + spacing
		draw_text_with_stroke(screen, no_text, self.font, (no_x, scores_y), stroke_color=(0, 255, 0))

		total_seconds = 60 - int(self.frame / 60)
		if total_seconds < 0:
			total_seconds = 0
		minutes = total_seconds // 60
		seconds = total_seconds % 60
		time_text = f"{minutes}:{seconds:02d}"

		# Couleurs
		orange = (255, 165, 0)
		white = (255, 255, 255)

		# Position chrono
		chrono_x = WIDTH // 2
		chrono_y = 50

		# Dessiner contour orange (offset autour du texte)
		for dx in [-2, -1, 0, 1, 2]:
			for dy in [-2, -1, 0, 1, 2]:
				if dx != 0 or dy != 0:
					contour_surf = self.font.render(time_text, True, orange)
					screen.blit(contour_surf, (chrono_x - contour_surf.get_width() // 2 + dx, chrono_y + dy))

		# Dessiner texte blanc par-dessus (centré)
		text_surf = self.font.render(time_text, True, white)
		screen.blit(text_surf, (chrono_x - text_surf.get_width() // 2, chrono_y))
