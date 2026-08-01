# Instagram followers pro Widgy

Automatická varianta pro profesionální Instagram účet. Skript uloží jednoduchý `instagram.json`, který může číst Widgy. Nejstabilnější je oficiální Instagram API, ale projekt umí běžet i bez Meta registrace přes veřejné fallbacky.

## Co z toho vznikne

Veřejný JSON endpoint:

```text
https://oliverblaha-hue.github.io/instagram-widgy-auto/instagram.json
```

Příklad obsahu:

```json
{
  "username": "oliver_blaha_gallery",
  "followers": 1234,
  "followers_display": "1 234",
  "following": 321,
  "posts": 87,
  "updated_at": "2026-07-31T20:00:00Z"
}
```

## Nejjednodušší postup

1. Repo už je vytvořené: `https://github.com/oliverblaha-hue/instagram-widgy-auto`.
2. GitHub Pages už publikuje JSON:
   `https://oliverblaha-hue.github.io/instagram-widgy-auto/instagram.json`.
3. Workflow **Update Instagram stats** běží automaticky každých 5 minut a dá se spustit ručně v záložce **Actions**.
4. Pro nejlepší spolehlivost můžeš později přidat secret:
   - název: `IG_ACCESS_TOKEN`
   - hodnota: tvůj dlouhodobý Instagram User Access Token
5. Pokud používáš starší Facebook/Page napojení místo Instagram Login, přidej i repository variable nebo secret:
   - název: `IG_USER_ID`
   - hodnota: tvoje Instagram User ID
   - volitelně variable `IG_API_HOST` nastav na `https://graph.facebook.com`

## Widgy

1. Otevři **Widgy**.
2. Vytvoř nový **Home Widget**.
3. Přidej text pro počet sledujících.
4. Jako data použij JSON endpoint z GitHub Pages.
5. Vyber hodnotu:

```text
followers_display
```

Můžeš přidat i:

```text
username
posts
following
updated_at
```

## Důležité

Nikdy nevkládej Instagram access token přímo do Widgy. Widget by ho mohl zbytečně vystavit. Token patří jen do GitHub Secretu `IG_ACCESS_TOKEN`.

Když `IG_ACCESS_TOKEN` chybí, skript automaticky použije veřejný profil `oliver_blaha_gallery`. Nejdřív zkusí veřejnou HTML stránku Instagramu. Pokud Instagram GitHub zablokuje, použije nouzově veřejnou cache Instastatistics. Je to zdarma a bez Meta registrace, ale číslo může být zpožděné a fallback se může rozbít, pokud se změní veřejné zdroje.
