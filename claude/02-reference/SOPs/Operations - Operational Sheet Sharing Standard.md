# Operations - Operational Sheet Sharing Standard

**Purpose:** Every operational sheet is editable by DVN and the admin team at all times.
No single-owner lockouts, no view-only surprises, no Excel-mode friction.

**Owner of this standard:** DVN. **Authorized to apply it:** Jenae.
**Cadence:** apply on every new operational sheet; audit quarterly.

---

## The rule (four lines)

1. **Operational sheets live on the Shared Drive** — never in one person's *My Drive*.
2. **Native Google Sheets** — not `.xlsx`. Convert on import.
3. **Access:** DVN + admin team (Jenae, Stephanie) = **Editor / Content manager**. Company domain = **Viewer** max.
4. **No sheet is owned by one person** in a way that locks everyone else out if that person is unavailable.

If a sheet can't be edited by Jenae today, it's out of standard — fix it before using it.

---

## Why — the June 2026 access audit

Pulled the live sharing on the core trackers. Two patterns:

| Sheet | Home | DVN | Jenae | Domain | Status |
|---|---|---|---|---|---|
| Pipeline Tracker | Shared Drive | Organizer | Full edit | Viewer | 🟢 correct |
| Commission Tracker | Shared Drive | Organizer | Full edit | Viewer | 🟢 correct |
| ✅ 2026 Listing Appointments Tracking | **My Drive (DVN)** | Owner | **No access** | Viewer | 🔴 locked |
| VNRE EOS System | **My Drive (DVN)** | Owner | **No access** | Viewer | 🔴 locked |

Root cause: the sheets DVN keeps in **personal My Drive** are shared **view-only to the
`thevannoygroup.com` domain** (a different domain than the `@vannoyre.com` logins), and Jenae
was never added. The Shared Drive trackers were already correct. Both locked files are also
`.xlsx`, which Drive opens in a clunky read-only-ish mode even with edit rights.

---

## Fix an existing sheet (60 seconds each)

**Best — move it to the Shared Drive.** Drag the file into the same Shared Drive as the
Pipeline / Commission trackers. Everyone there is already an editor; the lockout can't recur.

**In place (if it must stay in My Drive):** open → **Share** →
1. Add **Jenae@vannoyre.com** as **Editor**.
2. Change the domain from **Viewer → Editor**, or remove the domain grant and add people explicitly.
3. Confirm the owning login is the `@vannoyre.com` account the team actually uses.

**Always — convert Excel to Sheets:** **File → Save as Google Sheets**. Kills the `.xlsx`
friction and enables real-time co-editing.
> Conversion creates a **new file ID**. Send the new link to whoever maintains the Command
> Center so the data source is repointed (see tie-in below).

---

## New operational sheet — checklist

- [ ] Created **on the Shared Drive** (not My Drive).
- [ ] **Native Google Sheet** format.
- [ ] DVN + Jenae + relevant admin = **Editor / Content manager**.
- [ ] Domain set to **Viewer** only (or no domain grant).
- [ ] Named per convention and filed in the right folder.
- [ ] If it feeds the Command Center, its file ID is registered in the snapshot sources.

---

## Tie-in — the Operations Command Center

The dashboard reads these sheets as data sources (`command-center/data/snapshot.json` →
`meta.sources[].fileId`). **If a sheet is converted to Google Sheets or moved, its file ID
changes** — update the matching `fileId` in `snapshot.json` and re-run `python3 build.py`
so the Command Center keeps reading the live file. Keep this registry current:

| Block fed | Sheet | Refresh |
|---|---|---|
| `funnel` | 2026 Listing Appointments Tracking | edit snapshot.json |
| `pipeline.deals` | Pipeline Tracker | edit snapshot.json |
| `eos` | VNRE EOS System | edit snapshot.json |
| `finance` | QuickBooks (not a sheet) | `build.py --refresh-financials` |
