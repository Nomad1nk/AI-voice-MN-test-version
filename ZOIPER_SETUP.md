# Zoiper5 SIP Account Setup Guide

This guide walks you through adding a SIP account in Zoiper5 to register with your local Asterisk server running in WSL2.

## Quick Summary

- **SIP Server (Domain):** 127.0.0.1
- **SIP Port:** 5060
- **Username:** 100
- **Password:** 1234
- **Transport:** UDP
- **Status Expected:** Green checkmark (registered)

---

## Step-by-Step Setup in Zoiper5

### 1. Open Zoiper5 Account Manager

- Launch Zoiper5 on your Windows machine
- Click **Accounts** (or menu icon) on the left sidebar
- You should see a list of accounts (or an empty list if this is your first account)

### 2. Add a New SIP Account

- Click **Add** button (usually a green "+" or "Add" button at the bottom left)
- A dialog will open asking you to choose account type
- Select **SIP** (not IAX, not other types)

### 3. Fill in SIP Credentials

When the SIP account form opens, fill in these exact fields:

| Field Name    | Value     | Notes                                               |
| ------------- | --------- | --------------------------------------------------- |
| **Username**  | 100       | This is the extension number on Asterisk            |
| **Password**  | 1234      | Pre-shared secret configured in Asterisk            |
| **Domain**    | 127.0.0.1 | IP address of your WSL2 Asterisk server (localhost) |
| **SIP Port**  | 5060      | Default Asterisk PJSIP port                         |
| **Transport** | UDP       | Standard, most compatible                           |

### 4. Optional Advanced Settings (if Zoiper asks)

If you see an **Advanced** or **Settings** tab:

- **Registrar:** Leave blank (will default to Domain) OR set to `127.0.0.1:5060`
- **Outbound Proxy:** Leave blank
- **Auth Username:** Leave blank (same as Username by default)
- **Use TLS:** No (disable for local testing)
- **SRTP:** No (disable for local testing)
- **Codecs:** Ensure **G.711 ulaw** and/or **G.711 alaw** are enabled (check the Audio settings if available)

### 5. Save and Register

- Click **OK** or **Save** to save the account
- Zoiper should automatically attempt to register
- Watch the account status in the left sidebar:
  - ✅ **Green checkmark** = Successfully registered (good!)
  - ❌ **Grey X or red symbol** = Failed to register (we'll debug this)
  - ⏳ **Spinning icon** = Registering (wait a few seconds)

---

## If Registration Fails (Grey X or Error)

### Check Asterisk is Running (Windows PowerShell)

```powershell
# Test if Asterisk on WSL2 is listening on port 5060
Test-NetConnection -ComputerName 127.0.0.1 -Port 5060 -InformationLevel Detailed
```

Expected output: `TcpTestSucceeded : True`

### Watch Asterisk Logs (WSL2 Ubuntu shell)

Open a new Ubuntu terminal and run the Asterisk console:

```bash
sudo asterisk -rvvv
```

Then inside the `asterisk>` prompt, enable SIP logging:

```
pjsip set logger on
```

Now try to register Zoiper again. Paste the SIP REGISTER request and response here, and I'll help diagnose the issue.

---

## After Successful Registration

Once you see the green checkmark in Zoiper:

1. **Test a local call:**

   - Install MicroSIP or another softphone with account 200 / password 2000 on the same Asterisk
   - Dial 100 from that softphone
   - Zoiper (extension 100) should ring

2. **Test with Python ARI script:**
   - From Windows PowerShell, run:
     ```powershell
     cd C:\Users\nomad\receptionist-ai
     python -m pip install -r requirements.txt
     python python\ari_example.py
     ```
   - Call extension 100 from another softphone or Zoiper itself
   - The ARI script will answer and play "hello-world" sound

---

## Common Issues & Fixes

| Symptom                  | Likely Cause                           | Fix                                                                                 |
| ------------------------ | -------------------------------------- | ----------------------------------------------------------------------------------- |
| Grey X, 408 Timeout      | Asterisk not listening or port blocked | Confirm `sudo systemctl status asterisk` is running in WSL2; check Windows firewall |
| Grey X, 401 Unauthorized | Wrong password or username mismatch    | Verify username is exactly "100" and password is exactly "1234"                     |
| Registers but no audio   | Codec mismatch or RTP ports blocked    | Ensure G.711 ulaw is enabled in Zoiper; check firewall for UDP 10000-20000          |
| Connection refused       | Asterisk crashed or WSL2 network issue | Run `sudo asterisk -rvvv` in WSL2 to see if it's running; check WSL2 networking     |

---

## Asterisk Configuration Files (Reference)

These were created automatically in your workspace:

- `asterisk/pjsip.conf` - Defines extensions 100 and 200
- `asterisk/extensions.conf` - Dialplan; extension 100 routes to `Stasis(myapp)` for ARI handling
- `asterisk/ari.conf` - Enables ARI HTTP interface for Python control

You don't need to edit these for basic registration to work.

---

## Next: Connect Python App to Asterisk

Once Zoiper registers successfully, you can:

1. **Use the Python ARI script** (`python/ari_example.py`) to answer calls to extension 100
2. **Build custom dialplan** in `extensions.conf` to transfer calls, play prompts, record audio, etc.
3. **Integrate with your receptionist app** to handle call logic

See `asterisk/README.md` for more details on running the Python ARI example.
