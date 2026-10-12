# Single-player local development bridge (NOT multiplayer)

UTF-8 JSON Lines over loopback 127.0.0.1:8765. Exactly one `player` connection and one `adapter` connection can be active. The bridge has no lobby or joining feature.

- Player hello: `{"type":"hello","role":"player","player":"solo","secret":"LOCAL_SECRET"}`
- Event adapter hello: `{"type":"hello","role":"adapter","secret":"LOCAL_SECRET"}`
- Synthetic MWIII test event: `{"type":"event","payload":{"event_id":"kill1","event":"mwiii_kill","player":"solo","victim":"enemy"}}`
- Synthetic golf event: `{"type":"event","payload":{"event_id":"hole1","event":"golf_hole_completed","player":"solo","hole_id":"1","strokes":3,"par":4}}`
- Synthetic course hazard: `{"type":"event","payload":{"event_id":"hazard1","event":"golf_hazard_hit","player":"solo","hazard_id":"bumper"}}`
- Own-ball cast request: `{"type":"cast","powerup":"cruise_missile"}`

The bridge emits score, powerup, hazard and state messages. It applies **no actual game physics**. Test input is not proof of any MWIII event feed, and a local TCP exchange is not gameplay in GWYF.

Never publish local developer secrets. No multiplayer host/join or public server is supported.
