# Online RandomChris

This is the online version of RandomChris.

To run it locally:

1. `cd ai2\chris\web`
2. `npm.cmd run dev`
3. Open ` http://localhost:5173/` in any browser


## Technical Notes:

### Stack and architecture

- Built with React, TypeScript, and Vite. The game/session logic is kept separate from the UI in `src/engine`; editable configuration and profile loading are in `src/config`; React screens and browser persistence are in `src/ui`.
- This is a static, client-side application. There is no backend or account system.
- Bundled profiles and their cast, games, and prompts are loaded from `public/config/`. `public/config/profiles.json` selects the default profile and defines the available profiles and their data files. A profile can also be selected with the `?profile=<key>` URL parameter.
- Vite's base path is relative (`./`), so the built site can be served from a subdirectory as well as a domain root.

### Configuration and browser storage

- The Configuration dialog lets you manage the active cast, games, and prompts. Cast members and games can be disabled for a session without deleting them; game definitions also support player exclusions and host include/exclude lists.
- Custom configuration is saved in the browser's `localStorage`, separately for each profile. It overrides that profile's bundled defaults on the same browser and origin; it is not shared with other users or browsers.
- Use **Data → Export** to download a complete JSON backup or the individual `games.json`, `cast.txt`, and `prompts.txt` files. Import accepts a complete JSON export or those legacy files. Review imported data and press **Save changes** to apply it. **Reset to default** removes the saved override for the current profile.
- An in-progress session is also saved locally and can resume after a reload when the profile and its cast/game list are unchanged. Changing and saving configuration restarts the session. Clearing browser site data removes both the saved configuration and session.

### Session behavior

- Each session uses a shuffled game sequence that interleaves game categories; an optional priority category is scheduled in the third category position.
- Hosts and players are selected randomly with weights that favor cast members who have had fewer corresponding turns. Per-game host and player restrictions are applied before selection.
- A game's own prompt is used when present; otherwise a prompt is chosen from the profile's prompt list. A game with `nbr_players: 0` uses all eligible cast members other than the host.
- The session countdown begins with the first game. Transition and countdown sounds are played in the browser; users can mute them in the controls.

### Development

From this directory:

```sh
npm install
npm run dev
npm run build
npm test
npm run lint
```

The build runs TypeScript project checks before creating the static site in `dist/`. Tests use Vitest.

## Port to webserver

The web version is a static site, so it can be hosted by any web server that serves HTML, JavaScript, CSS, and static data files. No Node.js process or backend needs to run after building.

1. Build the site from the `web` directory:

   ```sh
   npm ci
   npm run build
   ```

2. Copy the **contents** of the generated `dist/` directory to the web root configured for the site. For example, if `chris.charlier-tang.com` is configured to serve `/var/www/chris.charlier-tang.com`, copy `dist/index.html`, `dist/assets/`, `dist/config/`, and the other files inside `dist/` there. Do not copy the `dist` folder itself as a nested directory unless that nested URL is intended.

3. Configure the domain's DNS to point to the server, and configure its virtual host to serve that web root over HTTPS. The server should serve `index.html` for `/` and preserve the static directory structure so the app can load its profile data and assets.

For an Nginx virtual host, the essential static-site configuration looks like this (replace the document root with the actual deployment path):

```nginx
server {
    listen 80;
    server_name chris.charlier-tang.com;

    root /var/www/chris.charlier-tang.com;
    index index.html;

    location / {
        try_files $uri $uri/ /index.html;
    }
}
```

Set up TLS for the domain and redirect HTTP to HTTPS using the web server's normal certificate-management process. After deployment, open the domain and verify that the app loads its profile data and assets. The relative asset base supports hosting at the domain root or under a subdirectory; for a subdirectory, copy the `dist/` contents into that directory and configure the server to serve it there.