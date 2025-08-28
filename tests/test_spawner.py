import unittest

from turkey_invaders.core.world import World
from turkey_invaders.systems.spawner import Spawner


class TestSpawner(unittest.TestCase):
    def setUp(self):
        self.world = World()
        self.world.width = 60
        self.world.height = 24
        self.spawner = Spawner(self.world)

    def test_formation_spawns_once(self):
        # First wave should be formation and spawn immediately
        self.assertEqual(self.spawner.wave_index, 0)
        self.spawner.update(1.0 / 60.0)
        enemies = list(self.world.by_kind.get("enemy", []))
        self.assertGreater(len(enemies), 0)
        # All enemies in this wave should be tagged with _wave = 0
        for e in enemies:
            self.assertEqual(getattr(e, "_wave", None), 0)

    def test_advance_to_next_wave(self):
        # Spawn formation
        self.spawner.update(0.016)
        # Clear enemies to trigger wave completion
        for e in list(self.world.by_kind.get("enemy", [])):
            e.alive = False
        self.world.remove_dead()
        # Advance time beyond completion threshold
        self.spawner.update(0.2)
        self.assertEqual(self.spawner.wave_index, 1)
        # Spawn some enemies from wave 2 over time (dive/mixed)
        for _ in range(60):
            self.spawner.update(1.0 / 30.0)
        enemies = list(self.world.by_kind.get("enemy", []))
        self.assertGreater(len(enemies), 0)
        for e in enemies:
            self.assertEqual(getattr(e, "_wave", None), 1)


if __name__ == "__main__":
    unittest.main()

