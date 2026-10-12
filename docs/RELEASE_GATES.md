# Release blockers: Combat Golf Solo

The single-player source prototype is NOT ready for a one-click Melty release.

1. Locate and verify installations of Golf With Your Friends (host) and Call of Duty: MWIII (required companion), their engines, current binaries and file layout.
2. Get Melty `game_info` and compatible loader metadata for both games.
3. Implement and test a real, permitted MWIII elimination event source. No fake kill-input substitute.
4. Implement verified golf scoring callbacks and identify the player's actual ball.
5. Apply UAV aiming guidance, Cruise Missile own-ball impulse and Juggernaut hazard shielding to actual game state, with appropriate feedback.
6. Build the plugin against actual installed game assemblies. Package all redistributable runtimes without game files.
7. Build a validated Melty installed-mode recipe with file mappings, both required games and needed companion launch.
8. Pass Melty `inspect_package`, `validate_recipe`, `one_click_check`, and the real in-game `test_release`.
9. Capture a genuine screenshot of these power-ups running in the installed game before submission.
10. Reuse the existing Melty draft and publish only after a functional install and test, plus final user authorization.

**No multiplayer setup is required:** no game hosting, second player, join link, or multiplayer recipe is part of this edition.

Run `python tools/preflight.py --stage release`. It intentionally fails while game hooks remain unverified. Don't change evidence flags without actually testing them.
