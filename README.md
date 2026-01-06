# Forest Click Adventure (PgZero)

Um jogo **point-and-click** (visão aérea) feito com **PgZero**: clique para mover o herói, colete todas as moedas e evite os slimes que patrulham seus territórios. Quando pegar todas as moedas, o **portal** aparece — entre nele para vencer.

## 📦 Estrutura de arquivos

```
forest_click_adventure_pack/
├─ game.py
├─ images/
│  ├─ hero_idle_0.png ... hero_idle_3.png
│  ├─ hero_move_0.png ... hero_move_5.png
│  ├─ slime_idle_0.png ... slime_idle_3.png
│  ├─ slime_move_0.png ... slime_move_3.png
│  ├─ coin.png
│  └─ portal.png
├─ music/
│  └─ bgm.wav
└─ sounds/
   ├─ click.wav
   ├─ pickup.wav
   └─ hit.wav
```

---

## 🧰 Instalação

Instale o PgZero:

```bash
py -m pip install pgzero
```

---

## ▶️ Como executar

Abra o terminal na pasta do projeto (onde está o `game.py`) e rode:

### Opção A (padrão)

```bash
py -m pgzrun game.py
```

### Opção B (runner alternativo no Windows)

Se a janela piscar e fechar, use:

```bash
py -m pgzero.runner game.py
```

---

## 🕹️ Controles

- **Clique do mouse**: define para onde o herói vai caminhar
- **ESC**: volta para o menu principal

---

## 🎯 Objetivo do jogo

1. Colete **todas as moedas** no mapa.
2. Evite encostar nos **slimes** (inimigos).
3. Ao coletar todas as moedas, o **portal** é ativado.
4. Encoste no portal para **vencer**.

Se encostar em um slime → **derrota**.

---

## 🔊 Áudio

- Música de fundo: `music/bgm.wav`
- Sons:
  - `sounds/click.wav` → clique em botões/menu
  - `sounds/pickup.wav` → coleta de moeda
  - `sounds/hit.wav` → colisão com inimigo

O menu permite ligar/desligar áudio.

---
