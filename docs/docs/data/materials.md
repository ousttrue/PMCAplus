[文化ヒナゲシ制作所雑記帳 PMCA材質リストv2.0の仕様について](http://matosus304.blog106.fc2.com/blog-entry-239.html)

```
PMCA Materials list v2.0

SETDIR ./parts/

[name] mt_hair
[comment] 髪の色

[ENTRY] 青色01
[tex]	mt_hair_bl01.png
[toon] 6 toon_mt_hair_bl01.bmp
[diff_rgb] 0.80 0.80 0.80
[spec_rgb] 0.08 0.22 0.37
[mirr_rgb] 0.37 0.65 0.63
[author] mato
```

# material の色などを交換する。

pmd の material は名前が無いので texture ファイル名をマテリアル名として代用する。
parts になる pmd の texture 名にファイル名ではなく、
material リストの `[name]` を設定しておく。

1. parts の組合せでモデルが構築される
2. material のリストが確定して、変換リストも確定する
3. material 変換リストの選択状態 `sel` により `texture` が確定し、他の diffuse なども確定する。
