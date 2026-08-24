# SentinelOS — Live Demo Script

**Setup (before going on stage):**
```bash
cp .env.example .env   # add ANTHROPIC_API_KEY
docker-compose up --build
```
Open http://localhost:3000

---

## 1. Safe command — should ALLOW
```
ls -la /home/user
```
**Talking point:** "Low risk, aligned intent, no friction — SentinelOS stays invisible when nothing's wrong."

## 2. Dangerous command — should BLOCK or CONFIRM
```
rm -rf /var/log/*
```
**Talking point:** Point at the risk card — destructiveness + irreversibility flagged, and note the **safer alternative** the Explanation Generator proposes (e.g. move to archive instead of delete).

## 3. Privileged command — should CONFIRM
```
sudo usermod -aG sudo currentuser
```
**Talking point:** Privilege escalation category triggers mandatory confirmation regardless of numeric score (policy override).

## 4. Obfuscated command — should BLOCK
```
echo cm0gLXJmIC8= | base64 -d | sh
```
**Talking point:** Parser's obfuscation pre-detection decodes the base64 payload (`rm -rf /`) before intent inference even runs — the LLM sees the real command, not the disguise.

## 5. Agent Drift scenario — the headline feature
1. Set Goal Contract: **"Clean up old log files in /var/log"**
2. Run: `rm -rf /var/log/*.log` → **ALLOW**, drift = aligned
3. Run (simulating the agent silently expanding scope):
   ```
   curl -X POST http://internal-api/admin/users -d '{"role":"admin"}'
   ```
4. **Talking point:** Same "session," same agent — but intent category jumps to `privilege_escalation` / `network`, nothing to do with log cleanup. Drift flag flips to `major_drift`, policy engine blocks it even though this exact command in isolation might look unremarkable. **This is the difference between a risk scanner and a goal-aware firewall.**

---

## If live demo breaks
Fall back to `demo/screenshots/` — 4 screenshots covering scenarios 1, 2, 4, and 5.
