# Bowling WebApp (in project root)

Deze webapp staat in de projectroot `C:\Code\1`.

Opmerking: er is nu ook een client-only (staatloos) modus die geen Node/npm of server vereist.

Optie A — Client-only (geen Node nodig)
- Open `C:\Code\1\Templates\index.html` direct in je browser (dubbelklik of sleep naar browser).
- De app slaat reserveringen op in je browser via `localStorage` (alleen toegankelijk in die browser op dit apparaat).

Optie B — Server (optioneel, als je Node/npm kunt draaien)
- Vanuit projectroot:

```powershell
cd C:\Code\1
npm install
npm start
```

De server luistert dan op `http://localhost:3000`.

Gebruik de client-only modus als je geen scripts kunt draaien op dit apparaat.
