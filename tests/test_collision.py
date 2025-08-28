import unittest

from turkey_invaders.core.world import World
from turkey_invaders.entities.player import Player
from turkey_invaders.entities.enemy import GruntEnemy
from turkey_invaders.entities.projectile import Projectile
from turkey_invaders.systems.collision import resolve_collisions


class TestCollision(unittest.TestCase):
    def setUp(self):
        self.world = World()
        self.world.width = 40
        self.world.height = 20

    def test_enemy_contacts_player(self):
        p = Player(self.world.next_id(), x=10, y=10)
        self.world.player = p
        self.world.add(p)
        e = GruntEnemy(self.world.next_id(), x=10, y=10, speed=0)
        self.world.add(e)
        lives_before = p.lives
        resolve_collisions(self.world)
        self.assertLess(p.lives, lives_before)
        self.assertFalse(e.alive)

    def test_player_projectile_hits_enemy(self):
        p = Player(self.world.next_id(), x=5, y=5)
        self.world.player = p
        self.world.add(p)
        e = GruntEnemy(self.world.next_id(), x=6, y=6, speed=0)
        self.world.add(e)
        proj = Projectile(self.world.next_id(), x=6, y=6, owner="player", vy=-10.0)
        self.world.add(proj)
        resolve_collisions(self.world)
        self.assertFalse(e.alive)
        self.assertFalse(proj.alive)

    def test_enemy_projectile_hits_player(self):
        p = Player(self.world.next_id(), x=8, y=8)
        self.world.player = p
        self.world.add(p)
        proj = Projectile(self.world.next_id(), x=8, y=8, owner="enemy", vy=+1.0)
        self.world.add(proj)
        lives_before = p.lives
        resolve_collisions(self.world)
        self.assertLess(p.lives, lives_before)
        self.assertFalse(proj.alive)


if __name__ == "__main__":
    unittest.main()

