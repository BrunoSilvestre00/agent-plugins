# Scaffold inicial — frontend React/TS

Projeto: **{ALVO}**

Cria só o esqueleto (pastas + configuração funcional) — nenhum
componente/domínio de exemplo. Toolchain modernizado (Vite/Vitest) em
vez do CRA legado do projeto que originou as skills — a estrutura de
pastas e os padrões de código (Redux, componente, formulário) são os
mesmos. O primeiro componente/domínio real do projeto usa as skills
`react-view-component-pattern`, `redux-domain-pattern`,
`react-hook-form-pattern`, `http-client-pattern`, `frontend-tdd` — este
comando só prepara o chão onde elas vão se aplicar.

## Passos

1. Confirme que o diretório atual está vazio ou é claramente o repo novo
   do projeto {ALVO} (se houver arquivos de outro projeto, PARE e pergunte).

2. Crie a estrutura de pastas (com `.gitkeep` nas que ficam vazias):

   ```
   src/components/common/.gitkeep
   src/components/core/.gitkeep
   src/components/ui/.gitkeep
   src/views/.gitkeep
   src/store/.gitkeep
   src/store/__mock__/.gitkeep
   src/hooks/.gitkeep
   src/utils/.gitkeep
   src/utils/tests/.gitkeep
   src/client/.gitkeep
   src/routes/.gitkeep
   src/layouts/.gitkeep
   ```

3. Crie `package.json` (gerenciador de pacote: **yarn** via Corepack —
   mesma escolha do projeto de referência do time; `packageManager`
   fixa a versão exata, Corepack instala sozinho, sem precisar vendorizar
   binário nenhum):

   ```json
   {
     "name": "{ALVO}",
     "private": true,
     "version": "0.1.0",
     "type": "module",
     "packageManager": "yarn@4.5.0",
     "scripts": {
       "dev": "vite",
       "build": "tsc -b && vite build",
       "lint": "eslint .",
       "test": "vitest run --passWithNoTests",
       "test:watch": "vitest"
     },
     "dependencies": {
       "react": "^18.3.0",
       "react-dom": "^18.3.0",
       "react-redux": "^9.1.0",
       "redux": "^5.0.0",
       "redux-thunk": "^3.1.0",
       "typesafe-actions": "^5.1.0",
       "immer": "^10.1.0",
       "react-router-dom": "^6.23.0",
       "react-hook-form": "^7.51.0",
       "styled-components": "^6.1.0",
       "axios": "^1.7.0"
     },
     "devDependencies": {
       "@testing-library/jest-dom": "^6.4.0",
       "@testing-library/react": "^16.0.0",
       "@types/react": "^18.3.0",
       "@types/react-dom": "^18.3.0",
       "@vitejs/plugin-react": "^4.3.0",
       "eslint": "^9.0.0",
       "jsdom": "^24.0.0",
       "prettier": "^3.3.0",
       "typescript": "^5.5.0",
       "vite": "^5.3.0",
       "vitest": "^1.6.0"
     }
   }
   ```

4. Crie `.yarnrc.yml`:

   ```yaml
   nodeLinker: node-modules
   ```

   `node-modules` (não PnP) — compatibilidade máxima com o resto do
   ecossistema (Vite, eslint, etc.) sem exigir suporte a PnP de cada
   ferramenta.

5. Crie `vite.config.ts` (path aliases equivalentes ao projeto de
   referência, `test` aponta pro Vitest):

   ```ts
   import { defineConfig } from 'vite';
   import react from '@vitejs/plugin-react';
   import path from 'node:path';

   export default defineConfig({
     plugins: [react()],
     resolve: {
       alias: {
         components: path.resolve(__dirname, './src/components'),
         store: path.resolve(__dirname, './src/store'),
         utils: path.resolve(__dirname, './src/utils'),
         hooks: path.resolve(__dirname, './src/hooks'),
       },
     },
     test: {
       environment: 'jsdom',
       setupFiles: ['./src/setupTests.ts'],
       globals: true,
     },
   });
   ```

6. Crie `src/setupTests.ts`:

   ```ts
   import '@testing-library/jest-dom';
   ```

7. Crie `tsconfig.json` (strict, baseUrl compatível com os aliases):

   ```json
   {
     "compilerOptions": {
       "target": "ES2022",
       "lib": ["ES2022", "DOM"],
       "module": "ESNext",
       "moduleResolution": "bundler",
       "jsx": "react-jsx",
       "strict": true,
       "baseUrl": "./src",
       "paths": { "components/*": ["components/*"] }
     },
     "include": ["src"]
   }
   ```

8. Crie `eslint.config.js` (flat config mínimo — React + TS + hooks):

   ```js
   import js from '@eslint/js';
   import tseslint from 'typescript-eslint';
   import react from 'eslint-plugin-react';
   import reactHooks from 'eslint-plugin-react-hooks';

   export default tseslint.config(
     js.configs.recommended,
     ...tseslint.configs.recommended,
     {
       plugins: { react, 'react-hooks': reactHooks },
       rules: { ...reactHooks.configs.recommended.rules },
     }
   );
   ```

9. Crie `src/store/store.ts` — wiring do Redux vazio, pronto para o
   primeiro domínio (`redux-domain-pattern`):

   ```ts
   import { applyMiddleware, combineReducers, legacy_createStore as createStore } from 'redux';
   import { thunk } from 'redux-thunk';

   const rootReducer = combineReducers({
     // Novo domínio? Adicione aqui — ver a skill redux-domain-pattern.
   });

   export const store = createStore(rootReducer, applyMiddleware(thunk));
   export type AppState = ReturnType<typeof rootReducer>;
   ```

10. Crie `src/client/index.ts` — cliente HTTP único (ver
    `http-client-pattern` — nunca crie uma segunda instância):

    ```ts
    import axios from 'axios';

    export const client = axios.create({
      baseURL: import.meta.env.VITE_API_BASE,
    });

    client.interceptors.request.use((config) => {
      const token = localStorage.getItem('token');
      if (token) config.headers.Authorization = `Bearer ${token}`;
      return config;
    });
    ```

11. Crie `src/App.tsx` — providers (Redux + Router), sem tema/auth
    específicos (adicione conforme o projeto precisar):

    ```tsx
    import { Provider } from 'react-redux';
    import { BrowserRouter } from 'react-router-dom';
    import { store } from 'store/store';

    export function App() {
      return (
        <Provider store={store}>
          <BrowserRouter>{/* rotas em src/routes */}</BrowserRouter>
        </Provider>
      );
    }
    ```

12. Crie `.github/workflows/ci.yml`:

    ```yaml
    name: CI
    on: [pull_request]
    jobs:
      lint-test:
        runs-on: ubuntu-latest
        steps:
          - uses: actions/checkout@v4
          - uses: actions/setup-node@v4
            with:
              node-version: "20"
          - run: corepack enable
          - run: yarn install --immutable
          - run: yarn lint
          - run: yarn test
    ```

13. Crie `ARQUIVO_CONFIG`:

    ```markdown
    # {ALVO}

    Frontend React/TS — Vite + Redux + styled-components. Convenções em
    `react-view-component-pattern`, `redux-domain-pattern`,
    `react-hook-form-pattern`, `http-client-pattern`, `frontend-tdd`,
    `frontend-code-review-conventions` (plugin `dev-patterns`).

    ## Dev Flow Config

    - jira_projects: <preencher>
    - status_ready: Ready for Dev
    - status_in_progress: In Progress
    - status_testing: Testing
    - base_branch: main
    - test_command: yarn test
    - lint_command: yarn lint
    ```

    `test_command`/`lint_command`/`base_branch` acima já são os valores
    reais que este scaffold acabou de configurar — não são placeholder.
    Só `jira_projects` e os nomes de status ficam genéricos aqui.

14. **Se o comando `dev-toolkit-setup` estiver disponível nesta sessão**
    (plugin `dev-toolkit` instalado — este scaffold não depende dele,
    mas se estiver presente, aproveite): invoque-o agora, passando
    `jira_projects` se o usuário já tiver informado. Ele detecta que
    `test_command`/`lint_command` já estão preenchidos (não pergunta de
    novo), consulta os status reais do workflow do Jira via Atlassian e
    completa a seção — bem melhor que os placeholders genéricos acima.
    Se o comando não estiver disponível, deixe os placeholders e avise
    no relatório final que rodar `dev-toolkit-setup` (caso o plugin seja
    instalado depois) substitui os nomes de status genéricos pelos reais.

15. Reporte ao usuário: estrutura criada, `corepack enable && yarn
    install` como próximo passo, preencher `.env`/`VITE_API_BASE` e —
    só se o passo 14 não tiver rodado o `dev-toolkit-setup` — preencher
    `jira_projects`/status na mão no ARQUIVO_CONFIG.

## Regras

- NÃO crie nenhum componente/view/domínio Redux de exemplo — isso é
  código de produto real, fora do escopo deste comando.
- NÃO rode `git init`/commit — deixe isso para o usuário decidir.
- Se o diretório já tiver conteúdo de outro projeto, PARE e pergunte.
