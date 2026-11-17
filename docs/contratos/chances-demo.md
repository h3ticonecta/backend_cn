# Contrato — Chances demo (casa × usuário)

Configuração **somente no backend** (Django Admin). O frontend **não envia** percentuais nas requisições de girar/apostar.

**Aplicável a:** Roleta, Fortune Gems, Wolf Gold (e campos no catálogo `Game` para todos os jogos ativos).

---

## 1. Formato `Chances`

```ts
type Chances = {
  percentual_casa: string; // decimal, 2 casas, ex. "55.00"
  percentual_usuario: string; // ex. "45.00"
};
```

| Regra | Valor |
|--------|--------|
| Faixa | `0.00` – `100.00` cada |
| Soma | `percentual_casa + percentual_usuario = 100.00` |
| Padrão (seed/migração) | `55.00` / `45.00` |
| Tipo JSON | sempre **string** (igual demais valores monetários da API) |

---

## 2. Catálogo — tipo `Game`

Presente em `GET /api/v1/home/`, `GET /api/v1/games/` e no objeto `card` de `GET /api/v1/games/{slug}/`.

```ts
type Game = {
  id: string;
  title: string;
  provider: string;
  category: string;
  badge: string | null;
  rtp: string;
  gradient: [string, string];
  icon: string;
  play: PlayMeta | null;
  percentual_casa: string;
  percentual_usuario: string;
};
```

Em jogos **somente vitrine** (`play: null`), os percentuais existem para configuração futura / exibição; a lógica de giro **não** usa esses valores até existir backend jogável.

---

## 3. Onde `chances` aparece (jogáveis)

| Endpoint | Caminho no JSON |
|----------|-----------------|
| `GET /api/v1/roleta/?mesa=…` | `mesa.chances` |
| `GET /api/v1/games/roleta-brasil/` | `roleta.mesa.chances` (e espelho no payload de config) |
| `GET /api/v1/slots/fortune-gems/?jogo=…` | `jogo.chances` |
| `GET /api/v1/games/fortune-gems/` | `slot.jogo.chances` |
| `GET /api/v1/slots/wolf-gold/?jogo=…` | `jogo.chances` |
| `GET /api/v1/games/wolf-gold/` | `slot.jogo.chances` |

Exemplo:

```json
"chances": {
  "percentual_casa": "55.00",
  "percentual_usuario": "45.00"
}
```

No catálogo, os mesmos valores vêm em `percentual_casa` / `percentual_usuario` no nível do `Game` (útil na grade sem abrir o config do jogo).

---

## 4. Semântica (UI e integração)

- **Por rodada/giro pago**, o servidor sorteia se o resultado deve **tentar favorecer o jogador** (`percentual_usuario`) ou a **casa** (`percentual_casa`).
- Não é RTP garantido nem previsível por sessão; não exponha como promessa regulatória.
- **Endpoints de ação** (`POST …/girar/`, `POST …/roleta/girar/`) — **sem alteração** de body ou resposta por causa das chances.
- Free spins / money respin (Wolf Gold) e giros sem cobrança **não** reaplicam o viés da mesma forma que o giro base pago.

Sugestões de UI (opcional):

- Badge “Demo” ou tooltip com os percentuais lidos do config.
- Esconder completamente — comportamento do jogo não depende disso no cliente.

---

## 5. Sincronização (Admin, informativo)

| Origem | Destino |
|--------|---------|
| `Game` com `play_kind` roleta/slot | Mesa/slot com mesmo `play_mesa_slug` (ou `slug`) |
| `RoletaMesa`, `FortuneGemsJogo`, `WolfGoldJogo` | Jogos do catálogo vinculados |

Comando manual: `python manage.py sync_game_chances` (ver README do backend).

---

## 6. Referências por jogo

| Jogo | Contrato específico |
|------|---------------------|
| Roleta | [roleta.md](./roleta.md) |
| Fortune Gems | [fortune-gems.md](./fortune-gems.md) |
| Wolf Gold | [wolf-gold.md](./wolf-gold.md) |
| Candy Cascade (Sweet Bonanza) | [candy-cascade.md](./candy-cascade.md) |