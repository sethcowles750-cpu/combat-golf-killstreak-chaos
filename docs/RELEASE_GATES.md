# Release gates (unverified)

These steps are mandatory before saying the project is a real Melty mashup:

1. **Actual games**: verify installed Golf With Your Friends and Call of Duty: Modern Warfare III (2023) on a Windows machine. Keep Golf With Your Friends as the host and MWIII as required companion unless the established Melty project selection says otherwise.
2. **Melty introspection**: obtain `game_info` for both games, `search_mashups`, and closest published `mashup_info` through Melty's authenticated tools. They were not reachable in the working environment. No account-risk claim is made from unverified Melty metadata.
3. **Real COD events**: demonstrate a permitted, supported MWIII source for unique, session-bound elimination events. Do not inject into MWIII, alter its game files, or bypass game security protections. If the source is unavailable, do not represent manual event input as real kills or publish as a two-game mashup.
4. **Real golf events**: inspect Unity runtime/assemblies of the user's GWYF installation. Implement Harmony (or other compatible loader) callbacks for authoritative completed holes, player IDs, and player-owned ball rigidbodies. Install a loader only after Melty verifies it can deploy it. Do not assume Mono without checking.
5. **Actual power-ups**: make UAV draw meaningful golf guidance, Cruise Missile apply a network-consistent impulse to a selected opponent ball, and Juggernaut block that impulse in the actual game. Test impact on round scoring and multiplayer host/clients.
6. **Server and client**: derive and synchronize a real multiplayer join method from game session capabilities. The local relay in this repository is not a working Internet join system. Use `setup_multiplayer` and test two actual copies of Golf With Your Friends connected to one round before claiming capacity, address, or join behavior.
7. **Packaging**: compile C# plugin from the actual game assemblies. Bundle permitted redistributable runtimes as needed and keep copyrighted game files out. Replace the Python development process with a self-contained, one-click-shipped component if needed. No game content or community packs may be copied into the upload.
8. **Melty validation**: use `inspect_package`, `validate_recipe`, `one_click_check`, and `test_release` to pass the real Melty install/play test. Update recipe from actual API schema and write the validated version to repository root as `melty.json` only after it passes.
9. **Media**: capture a real screen recording or screenshot of this exact build running in an installed game. Do not substitute a mockup or test script output.
10. **Publication**: build release archive, upload real bytes/SHA-256 and media, pass the test; only then seek final publication authorization and publish. Nothing has been submitted or published.

Local release preflight runs `python tools/preflight.py --stage release` and intentionally fails on 6 unverified hooks, unverified game installs, and unverified golf systems. Do not flip those cells to true without evidence.
