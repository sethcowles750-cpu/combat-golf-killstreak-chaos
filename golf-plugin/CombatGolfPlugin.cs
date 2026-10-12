// SOURCE-ONLY PLUGIN SCAFFOLD. Not tested in Golf With Your Friends.
// A game-version-specific, verified ball/hole adapter is required before release.
using System;
using System.Collections.Concurrent;
using System.IO;
using System.Net.Sockets;
using System.Text;
using System.Threading;
using BepInEx;
using BepInEx.Configuration;
using UnityEngine;

namespace CombatGolf
{
    [BepInPlugin("gg.combatgolf.killstreakchaos", "Combat Golf: Killstreak Chaos", "0.1.0")]
    public class CombatGolfPlugin : BaseUnityPlugin
    {
        [Serializable] private class Hello { public string type = "hello"; public string role; public string player; public string secret; }
        [Serializable] private class Cast { public string type = "cast"; public string powerup; public string target; }
        [Serializable] private class GameEvent { public string event_id; public string event; public string player; public string hole_id; public int strokes; public int par; }
        [Serializable] private class GameEventPacket { public string type = "event"; public GameEvent payload; }
        [Serializable] private class Incoming { public string type; public string player; public string target; public string powerup; public string effect; public bool blocked; public float strength; public int duration_seconds; public int points_remaining; public string message; }
        private ConfigEntry<string> _playerId;
        private ConfigEntry<string> _opponentId;
        private ConfigEntry<bool> _hostGolfAdapter;
        private readonly ConcurrentQueue<string> _inbox = new ConcurrentQueue<string>();
        private readonly object _writeLock = new object();
        private TcpClient _connection;
        private StreamWriter _writer;
        private TcpClient _eventConnection;
        private StreamWriter _eventWriter;
        private string _status = "Starting local dev connection";
        private string _lastAction = "In-game ball and scoring hooks are not implemented";
        private volatile bool _running;
        private int _streakBalance;

        private void Awake()
        {
            _playerId = Config.Bind("Development", "PlayerId", "alpha", "Must match the host relay's actual player ID; not auto-synced to Golf yet.");
            _opponentId = Config.Bind("Development", "OpponentId", "bravo", "Development-only target ID for Cruise Missile.");
            _hostGolfAdapter = Config.Bind("Development", "HostGolfAdapter", false, "Host only: send verified hole events once a game-specific hook is added.");
            string secret = Environment.GetEnvironmentVariable("COMBAT_GOLF_DEV_SECRET");
            if (String.IsNullOrEmpty(secret))
            {
                _status = "No DEV secret set; no network connection";
                return;
            }
            _running = true;
            Thread thread = new Thread(() => ConnectAndRead(secret));
            thread.IsBackground = true;
            thread.Start();
        }

        private void ConnectAndRead(string secret)
        {
            try
            {
                _connection = new TcpClient("127.0.0.1", 8765);
                NetworkStream stream = _connection.GetStream();
                _writer = new StreamWriter(stream, new UTF8Encoding(false)) { AutoFlush = true };
                _writer.WriteLine(JsonUtility.ToJson(new Hello { role = "player", player = _playerId.Value, secret = secret }));
                if (_hostGolfAdapter.Value)
                {
                    _eventConnection = new TcpClient("127.0.0.1", 8765);
                    _eventWriter = new StreamWriter(_eventConnection.GetStream(), new UTF8Encoding(false)) { AutoFlush = true };
                    _eventWriter.WriteLine(JsonUtility.ToJson(new Hello { role = "adapter", secret = secret }));
                }
                _inbox.Enqueue("Connected to LOCAL development relay");
                using (StreamReader reader = new StreamReader(stream, Encoding.UTF8))
                {
                    string line;
                    while (_running && (line = reader.ReadLine()) != null) _inbox.Enqueue(line);
                }
            }
            catch (Exception ex) { _inbox.Enqueue("Local relay failed: " + ex.Message); }
        }

        private void Update()
        {
            string line;
            while (_inbox.TryDequeue(out line))
            {
                if (!line.StartsWith("{")) { _status = line; continue; }
                try
                {
                    Incoming msg = JsonUtility.FromJson<Incoming>(line);
                    if (msg.type == "welcome") _status = "Connected (development only)";
                    else if (msg.type == "error") _status = "Relay error: " + msg.message;
                    else if (msg.type == "powerup")
                    {
                        if (msg.player == _playerId.Value) _streakBalance = msg.points_remaining;
                        if (msg.blocked) _lastAction = "Cruise Missile intercepted by Juggernaut";
                        else _lastAction = msg.powerup + " -> " + msg.target + " (PHYSICS HOOK PENDING)";
                        // IMPORTANT: Do not fake game physics. A verified adapter needs to
                        // locate the actual target ball, handle ownership and replicate effects.
                    }
                }
                catch (Exception ex) { Logger.LogWarning("Invalid relay packet: " + ex.Message); }
            }
            if (Input.GetKeyDown(KeyCode.F6)) TryCast("uav", null);
            if (Input.GetKeyDown(KeyCode.F7)) TryCast("cruise_missile", _opponentId.Value);
            if (Input.GetKeyDown(KeyCode.F8)) TryCast("juggernaut", null);
        }

        private void TryCast(string power, string target)
        {
            if (_writer == null) { _status = "Not connected to local relay"; return; }
            try
            {
                lock (_writeLock) _writer.WriteLine(JsonUtility.ToJson(new Cast { powerup = power, target = target }));
            }
            catch (Exception ex) { _status = "Cannot send: " + ex.Message; }
        }

        // FUTURE HOOK: call only when the host has verified an actual
        // Golf With Your Friends hole completion from a real game assembly.
        public void OnVerifiedGolfHoleCompleted(string playerId, string courseAndHoleId, int strokes, int par)
        {
            if (!_hostGolfAdapter.Value || _eventWriter == null) return;
            var e = new GameEvent {
                event_id = "golf-" + Guid.NewGuid().ToString("N"),
                event = "golf_hole_completed", player = playerId,
                hole_id = courseAndHoleId, strokes = strokes, par = par
            };
            try { lock (_writeLock) _eventWriter.WriteLine(JsonUtility.ToJson(new GameEventPacket { payload = e })); }
            catch (Exception ex) { Logger.LogWarning(ex.Message); }
        }

        private void OnGUI()
        {
            // This is a genuine Unity overlay scaffold but NOT verified in GWYF.
            GUI.Box(new Rect(12, 12, 480, 103), "COMBAT GOLF [SOURCE-ONLY DEV PLUGIN]");
            GUI.Label(new Rect(22, 35, 460, 23), _status);
            GUI.Label(new Rect(22, 55, 460, 23), "F6 UAV | F7 Cruise Missile | F8 Juggernaut | balance: " + _streakBalance);
            GUI.Label(new Rect(22, 75, 460, 34), _lastAction);
        }

        private void OnDestroy()
        {
            _running = false;
            try { _connection?.Close(); _eventConnection?.Close(); }
            catch (Exception) { }
        }
    }
}
