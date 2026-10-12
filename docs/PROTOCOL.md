# Local development wire protocol v0 (NOT Internet multiplayer)

UTF-8 JSON Lines over TCP on **127.0.0.1:8765** (all frames under 8192 bytes).
The server owns the Match scoring state. Every peer sends `hello` first with a local development secret.

`{"type":"hello","role":"player","player":"alpha","secret":"LOCAL_SECRET"}`

`{"type":"hello","role":"adapter","secret":"LOCAL_SECRET"}`

Only an `adapter` may report real-game events. Currently *no adapter reading an installed game exists*; the CLI's `kill` and `hole` commands create **explicitly fake development events**:

`{"type":"event","payload":{"event_id":"unique-session-1","event":"mwiii_kill","player":"alpha","victim":"enemy"}}`

`{"type":"event","payload":{"event_id":"unique-session-2","event":"golf_hole_completed","player":"alpha","hole_id":"course1:1","strokes":3,"par":4}}`

Any connected player may request an ability, but the server authoritatively validates points/cooldowns/targets:

`{"type":"cast","powerup":"cruise_missile","target":"bravo"}`

The server broadcasts `score`, `powerup`, and `state` frames to connected peers; it does not apply Unity physics itself. The game plugin currently displays a development overlay only.

**Threat model:** loopback-only with a shared *developer* secret, no anti-cheat, no identity attestation, no protection from other local processes. This is not a trustworthy public tournament service. For actual multiplayer, bind identities and events to verified game sessions and use the game's legitimate networking/lobby mechanisms.
