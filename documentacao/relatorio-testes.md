# Relatório da suíte de testes

Execução em 28 de novembro de 2026, na raiz do repositório:

```bash
.venv-run/bin/pytest tests --ignore=tests/review -q --no-cov --tb=line
```

Resultado: **209 passaram, 5 falharam**, em 6 min 44 s. A suíte usa `DATABASE_URL_TESTE` e recusa seguir se essa URL for a base de produto. Cada teste recria o esquema nessa base isolada.

A primeira coleta de `tests` inteiro parou em `tests/review/test_module_shape.py` porque o pacote `radon` não está instalado. A revisão de ciclos foi rodada à parte e falhou. A revisão de mutação (`mutmut`) não foi executada.

## Falhas

| Teste | O que aconteceu |
| --- | --- |
| `tests/test_casca_visual.py::test_menu_resumo_e_impressao` | O menu, o logo e o link **IMPRIMIR VOO** passaram. A busca por `<section id="resumo">` não achou o bloco: o relatório usa `<header id="resumo">`. |
| `tests/test_orientacao.py::test_tela_e_pdf_usam_o_texto_do_piloto` | A página do plano não contém mais o trecho «Informe de onde sai» de `documentacao/piloto.md`. O texto de orientação deixou de ser despejado no relatório. |
| `tests/test_tempo.py::test_taf_e_consultado_quando_metar_nao_tem_publicacao` | O METAR vazio continua sem inventar observação e o TAF da resposta de teste entra no resultado. A ordem gravada das URLs foi `metar`, `SBJD`, `taf`. O teste esperava só `metar` e `taf`. A consulta ao TAF da REDEMET, no endereço que leva o indicativo, acontece antes do TAF do Aviation Weather Center. |
| `tests/test_tempo.py::test_meteorologia_rota_escolhe_estacao_regional_mais_proxima_e_desempata` | A escolha da estação regional mais próxima continua no resultado. A lista de chamadas ganhou um `taf` extra da REDEMET antes da busca por caixa geográfica. |
| `tests/test_tempo.py::test_tela_mostra_boletim_atual_e_pdf_preserva_o_snapshot` | A página mostra o boletim novo e não mostra o METAR antigo. No PDF, a sequência `METAR SBJD 121200Z 18010KT` não aparece contínua nos bytes do arquivo. |
| `tests/review/test_dependencies.py::test_imports_have_no_new_cycles` | Há ciclo novo: `servidor.pdf_plano` importa `servidor.planos`, e `servidor.planos` importa `servidor.pdf_plano`. |

## Como a suíte está armada

| Arquivo | Papel |
| --- | --- |
| `tests/conftest.py` | Sobe o Flask de teste, troca `DATABASE_URL` pela base de teste, recria as tabelas e oferece o cliente HTTP e o cadastro |
| `tests/conftest_rota.py` | Cria a emenda fictícia S0A1, S0B2 e S0C3 e os aviões de exercício |
| `documentacao/piloto.md` | Texto que `test_orientacao.py` compara com a tela e com o PDF |
| `documentacao/operacao.md` | Texto que `test_operacao_doc.py` revista em busca de segredo |
| `pyproject.toml` | Limites lidos pela revisão de ciclos, tamanho e mutação |

Os testes de rede não saem para a internet: um `getter` ou um `monkeypatch` devolve a resposta falsa.

## Acesso e sessão

Arquivo: `tests/test_acesso.py`. Exercita `servidor/auth.py`, a sessão do Flask e as páginas `templates/entrar.html`, `templates/cadastro.html` e `templates/perfil.html`.

- `test_senha_curta_nao_cria` — senha com menos de 8 caracteres não cria piloto.
- `test_cadastro_exige_nome_de_exibicao` — cadastro sem nome de exibição é recusado.
- `test_cadastro_apara_nome_de_exibicao` — espaços nas pontas do nome são removidos.
- `test_cadastro_html_cria_sessao_e_abre_painel` — o formulário HTML cria a sessão e abre o painel.
- `test_cadastro_recusa_nome_vazio_ou_acima_do_limite` — nome vazio ou longo demais não grava.
- `test_edicao_de_perfil_altera_somente_o_piloto_autenticado` — a troca de nome vale só para quem está na sessão.
- `test_edicao_de_perfil_recusa_nome_invalido_sem_alterar_valor` — nome inválido deixa o valor anterior.
- `test_edicao_html_de_perfil_salva_nome_e_redireciona` — o formulário salva e volta à tela.
- `test_edicao_html_invalida_nao_confirma_sucesso` — edição inválida não mostra sucesso.
- `test_alterar_senha_exige_senha_atual_e_confirmacao_igual` — senha nova exige a atual e a confirmação igual.
- `test_entrar_html_autentica_e_abre_painel` — entrar pela página abre o painel.
- `test_perfil_exige_sessao` — perfil sem sessão não abre.
- `test_mensagem_unica_e_bloqueio` — identificação errada, senha errada e bloqueio usam a mesma mensagem; cinco recusas bloqueiam.
- `test_sair_encerra_sessao` — sair encerra a sessão na API.
- `test_sair_html_encerra_sessao_e_redireciona` — sair pela página redireciona e o título é «Entrar — Plano de Voo».
- `test_oito_horas_sem_uso` — sessão parada por 8 horas expira.

Arquivo: `tests/test_isolamento.py`. Exercita `servidor/planos_consulta.py`.

- `test_piloto_nao_ve_plano_alheio` — o segundo piloto não lê, altera nem apaga o plano do primeiro.

Arquivo: `tests/test_migracao_perfil.py`. Exercita a migração Alembic do nome de exibição.

- `test_migracao_preenche_nome_de_exibicao_sem_alterar_credenciais` — a migração preenche o nome e não mexe na senha.

## Tela do piloto

Arquivo: `tests/test_tela_piloto.py`. Exercita `templates/plano.html`, `templates/plano_novo.html`, `templates/painel.html`, `app.py` e o JavaScript do mapa.

- `test_recusa_devolve_os_valores_e_nao_pede_hora_futura` — recusa devolve o que foi digitado e não exige hora futura.
- `test_formulario_agrupa_campos_em_duas_linhas_responsivas` — origem, destino, data e pesos ficam em linhas que cabem na tela.
- `test_sem_rab_selecao_de_aeronave_vazia_e_envio_desativado` — sem extrato RAB a lista factual fica vazia e o envio não segue.
- `test_tela_novo_plano_oferece_categoria_sintetica_sem_rab` — sem RAB a categoria sintética continua disponível.
- `test_hora_passada_mostra_o_pedido` — hora que já passou mostra o pedido, não some.
- `test_busca_de_aerodromo_nao_devolve_a_lista_inteira` — a busca devolve só o que combina com o texto.
- `test_filtro_casa_codigo_ou_nome_sem_acento` — o filtro aceita código ou nome, sem depender de acento.
- `test_combobox_seleciona_com_teclado_e_clique_e_recusa_texto_livre` — a escolha é por teclado ou clique; texto livre não vale.
- `test_painel_oferece_editar_e_apagar_somente_o_proprio_plano` — editar e apagar aparecem só no plano daquele piloto.
- `test_painel_mostra_partida_na_linha_do_titulo_sem_rotulo_de_estado` — a partida aparece na linha do plano, sem rótulo de estado.
- `test_atualizar_recalcula_o_relatorio_sem_texto_no_botao` — o botão de atualizar recalcula e não leva texto no ícone.
- `test_alterar_recalcula_o_mesmo_plano_e_recusa_nao_substitui` — alterar recalcula o mesmo plano; uma recusa não troca o gravado.
- `test_tabela_vazia_nao_aparece_e_mapa_avisa_a_carta` — sem trecho a tabela some e o mapa avisa a carta.
- `test_detalhe_plano_apresenta_rota_completa_contatos_e_alerta_destacado` — a rota completa, o alerta e a ausência do cartão de contato na página.
- `test_plano_com_varios_trechos_apresenta_fichas_e_remove_checklist_da_tela` — cada trecho vira ficha e o checklist não fica na página.
- `test_mapa_recebe_somente_os_pontos_de_cada_trecho_sem_mensagens_redundantes` — o mapa recebe os dois pontos de cada trecho, sem texto repetido.
- `test_mapa_exibe_um_unico_controle_de_radar_e_wac_pdf_validada` — um controle de radar e a carta WAC só quando o PDF oficial existe.
- `test_resolvedor_radar_prioriza_rainviewer_e_usa_redemet_se_indisponivel` — RainViewer vem primeiro; REDEMET só entra se ele falhar.
- `test_resolvedor_satelite_exige_sessao_propriedade_e_nao_expoe_chave` — satélite exige sessão e plano próprio e não devolve a chave.
- `test_controles_do_mapa_nao_expoem_openaip` — o controle OpenAIP não aparece nesta tela.
- `test_fichas_mostram_metar_e_taf_dos_aerodromos_do_trecho` — cada ficha mostra METAR e TAF da saída e da chegada, inclusive o regional.
- `test_controles_do_mapa_sao_compactos_e_nao_exibem_estados_redundantes` — os botões do mapa ficam compactos, sem estado repetido.
- `test_pagina_plano_omite_tabela_de_procedencia` — a página não mostra a tabela extensa de fontes.
- `test_plano_antigo_nao_mostra_detalhe_de_configuracao_do_radar` — plano antigo não exibe configuração interna do radar.
- `test_provedor_radar_nao_e_consultado_ao_abrir_o_plano` — abrir o plano não chama o provedor de radar.
- `test_rotas_rainviewer_exigem_sessao_e_propriedade_do_plano` — o tile de chuva exige sessão e o plano daquele piloto.
- `test_detalhe_atualiza_meteorologia_html_e_json_sem_persistir` — reabrir o plano busca boletim novo na tela e não grava por cima do snapshot.
- `test_tile_openaip_exige_sessao_e_propriedade_do_plano` — o tile OpenAIP exige sessão e plano próprio.
- `test_checklist_nao_aparece_na_tela_do_plano` — o checklist sugerido não é desenhado na página.
- `test_programacao_por_trecho_mostra_horarios_solares_e_pernoite` — o infográfico e a rota mostram hora, dia seguinte e pernoite.
- `test_plano_legacy_e_agenda_indisponivel_nao_inventam_horarios` — plano antigo ou sol ausente não ganha horário inventado.

Arquivo: `tests/test_casca_visual.py`. Exercita `templates/base.html`, `static/css/tailwind.css` e o emblema.

- `test_folha_tailwind_local_e_compilada` — a página usa a folha local, não um CSS de CDN.
- `test_planta_e_emblema_em_todas_as_paginas` — planta e emblema aparecem no conjunto de páginas.
- `test_logo_no_cartao_de_autenticacao_sem_logo_no_cabecalho` — no acesso o logo fica no cartão, não no cabeçalho.
- `test_vidro_na_entrada_e_no_plano_novo` — entrada e novo plano usam o cartão de vidro.
- `test_espera_nao_calcula_voo` — a página de espera não calcula voo no navegador.
- `test_menu_resumo_e_impressao` — menu, logo de 140 px e impressão no resumo. **Falhou** na busca por `section#resumo`.
- `test_todo_card_no_vidro_esfumacado_sem_vazar` — cartões ficam no vidro, sem vazar estilo.
- `test_menu_global_nao_exibe_aviso_de_impressao` — o aviso de impressão não entra no menu global.

Arquivo: `tests/test_orientacao.py`. Compara a tela e o PDF com `documentacao/piloto.md`.

- `test_tela_e_pdf_usam_o_texto_do_piloto` — **falhou** porque «Informe de onde sai» não está mais na página do plano.

Arquivo: `tests/test_historico.py`. Exercita alterar e apagar em `servidor/planos.py`.

- `test_editar_recalcula_e_apagar_pede_confirmacao` — editar recalcula; apagar sem confirmação não remove.

## Rota, cálculo e programação

Arquivo: `tests/test_calculo.py`. Exercita `servidor/calculo.py`.

- `test_componente_de_vento_separa_proa_e_cauda` — componente positivo é proa e negativo é cauda.
- `test_ficha_reune_km_pesos_e_reserva_ja_calculados` — a ficha junta quilômetros, pesos e a reserva de 30 minutos.
- `test_grandeza_tem_unidade_e_fonte` — cada grandeza sai com unidade e fonte.
- `test_peso_acima_do_mtow_da_aeronave_inaceitavel` — peso acima do máximo de decolagem não é aceito.
- `test_origem_igual_destino_nao_grava` — origem igual ao destino não grava plano.
- `test_manual_incompleto_nao_grava` — aeronave sem os campos técnicos não gera conta.
- `test_sem_vento_nao_publica_velocidade_de_solo` — sem vento não aparece velocidade em relação ao solo.
- `test_vento_disponivel_publica_a_fonte_do_produto` — com vento, a fonte do produto fica na grandeza.

Arquivo: `tests/test_rota.py`. Exercita `servidor/rota.py` e a gravação em `servidor/planos.py`.

- `test_busca_com_muitos_aerodromos_poda_rotas_fora_do_otimo` — a busca corta ramos piores que o melhor já achado.
- `test_direto_unico_sem_credito_de_cauda` — trecho direto único não ganha crédito de vento de cauda.
- `test_escala_quando_direto_nao_cabe` — se o direto não cabe no combustível, entra uma escala.
- `test_busca_meteorologia_uma_vez_por_aerodromo_da_rota` — cada aeródromo da rota é consultado uma vez.
- `test_rota_impossivel_gravada` — rota que não cabe é gravada como inaceitável, com motivo.
- `test_lista_local_nao_permite_plano_sem_emenda_rotaer_vigente` — sem emenda vigente não há plano factual.
- `test_post_e_put_recusam_aeronave_fora_da_selecao_vigente` — criar e alterar recusam aeronave fora da lista.
- `test_perfil_sintetico_exige_emenda_rotaer_vigente` — o perfil sintético também precisa da emenda para a rota.
- `test_perfil_sintetico_pode_ser_calculado_sem_rab` — o sintético calcula mesmo sem extrato RAB.
- `test_empate_prefere_menos_escalas_e_depois_distancia` — empate de tempo fica com menos escalas e, de novo, com a mais curta.
- `test_vento_de_cauda_nao_estende_o_alcance_em_ar_calmo` — o alcance de planejamento não cresce com vento de cauda.
- `test_rota_fuel_based_remains_available_for_daylight_scheduler` — a rota por combustível continua disponível para a agenda diurna.
- `test_plano_persiste_programacao_calculada_pelo_servidor` — a programação gravada é a que o servidor calculou.

Arquivo: `tests/test_programacao.py`. Exercita `servidor/programacao.py`.

- `test_partida_antes_do_nascer_e_adiada_sem_pernoite` — saída antes do nascer espera o sol, sem pernoite.
- `test_chegada_exatamente_no_por_do_sol_e_aceita` — chegar no instante do pôr do sol é aceito.
- `test_excesso_do_por_do_sol_tenta_so_o_proximo_nascer_e_registra_pernoite` — passar do pôr do sol adia ao nascer seguinte e registra pernoite.
- `test_sequencia_de_trechos_registra_pernoite_no_aerodromo_da_segunda_perna` — o pernoite fica no aeródromo em que a viagem dorme.
- `test_uma_hora_de_abastecimento_separa_a_chegada_da_partida_seguinte` — a escala separa chegada e partida seguinte em 1 hora.
- `test_falta_de_dados_solares_invalida_agenda_sem_inventar_horarios` — sem sol a agenda fica indisponível, sem horário inventado.
- `test_trecho_que_nao_cabe_apos_uma_tentativa_fica_indisponivel` — uma tentativa de adiar que ainda não cabe encerra a agenda.
- `test_cache_solar_e_limitado_a_mesmo_aerodromo_e_data` — o cache do sol não reutiliza outro aeródromo nem outro dia.

## Meteorologia, mapa e catálogo

Arquivo: `tests/test_tempo.py`. Exercita `servidor/tempo.py`.

- `test_corpo_vazio_fica_indisponivel` — resposta vazia não vira boletim.
- `test_falha_de_rede_fica_indisponivel` — erro de rede fica indisponível.
- `test_sem_dado_nao_inventa_valor` — campo ausente não é preenchido.
- `test_taf_e_consultado_quando_metar_nao_tem_publicacao` — **falhou** na ordem das URLs; o TAF de teste ainda entra no resultado.
- `test_taf_permanece_disponivel_quando_consulta_metar_falha` — falha do METAR não apaga um TAF válido.
- `test_falha_no_taf_nao_remove_metar_valido` — falha do TAF não apaga um METAR válido.
- `test_taf_redemet_prioriza_mensagem_valida_mais_recente` — entre TAFs válidos da REDEMET fica o mais recente.
- `test_taf_redemet_rejeita_icao_divergente_e_faz_fallback_awc` — TAF de outro indicativo é rejeitado e o AWC entra.
- `test_falha_taf_redemet_e_awc_preserva_metar_valido` — as duas fontes de TAF falham e o METAR permanece.
- `test_metar_direto_tem_prioridade_sobre_busca_regional` — METAR do próprio indicativo dispensa a busca regional.
- `test_meteorologia_rota_escolhe_estacao_regional_mais_proxima_e_desempata` — **falhou** na contagem de chamadas; a estação mais próxima, com desempate pelo indicativo, continua a regra.
- `test_meteorologia_rota_aceita_50_nm_e_rejeita_estacao_mais_distante` — 50 NM entra; além disso, não.
- `test_meteorologia_rota_rejeita_metar_acima_de_50_nm` — estação além de 50 NM não é atribuída.
- `test_meteorologia_rota_nao_busca_regional_sem_coordenadas_validas` — sem coordenada válida não há busca regional.
- `test_metar_preserva_campos_estruturados_opcionais_sem_alterar_o_original` — campos extras são guardados e o texto original não muda.
- `test_metar_nao_cria_campos_estruturados_ausentes_ou_nulos` — nulo ou ausente não vira campo.
- `test_buscar_consulta_uma_vez_por_aerodromo_distinto` — `buscar` não repete o mesmo aeródromo.
- `test_meteorologia_rota_consulta_cada_aerodromo_distinto_uma_vez` — a rota meteorológica também consulta cada um uma vez.
- `test_campos_metar_em_portugues_mantem_unidades_e_codigos_da_fonte` — a leitura sai em português, com a unidade e o código da fonte.
- `test_campos_taf_separa_grupos_e_preserva_periodos` — BECMG, TEMPO e FM viram grupos, com o período original.
- `test_taf_becmg_periodo_e_temperatura_nao_quebram_o_grupo` — período, TX e TN não partem o grupo nem o texto.
- `test_campos_taf_sem_mensagem_nao_inventa_grupos` — TAF vazio não ganha grupo.
- `test_fenomenos_metar_e_taf_incluem_explicacao_sem_inventar_desconhecidos` — fenômeno conhecido ganha explicação; código desconhecido fica sem invenção.
- `test_campos_metar_ausentes_sao_marcados_sem_inferencia` — campo que a fonte não mandou não é inferido.
- `test_radar_sem_chave_informa_motivo` — sem chave REDEMET o radar informa o motivo.
- `test_radar_sem_cobertura_geografica_informa_motivo` — quadro que não cobre o trecho informa o motivo.
- `test_radar_com_falha_da_fonte_informa_motivo` — falha da fonte informa indisponível.
- `test_satelite_seleciona_frame_mais_recente_e_limites_da_fonte` — o satélite usa o frame mais recente e os limites publicados.
- `test_satelite_sem_chave_ou_metadados_validos_fica_indisponivel` — sem chave ou sem metadados válidos não há camada.
- `test_satelite_com_falha_de_rede_fica_indisponivel` — falha de rede não inventa imagem.
- `test_vento_so_quando_a_mensagem_cobre_a_rota` — vento de área só entra se a mensagem cobre o trecho.
- `test_cartas_wac_sao_consultadas_por_aerodromo_e_ordenadas_na_rota` — a carta é pedida por aeródromo e ordenada na rota.
- `test_carta_nao_infere_cobertura_por_bounds_nao_documentados` — limite que a fonte não documentou não vira cobertura.
- `test_cartas_wac_ficam_indisponiveis_se_um_aerodromo_nao_tiver_indice` — falta de índice em um aeródromo torna a carta indisponível.
- `test_tela_mostra_boletim_atual_e_pdf_preserva_o_snapshot` — **falhou** ao procurar o METAR antigo como texto contínuo no PDF. A página mostra o boletim atual.

Arquivo: `tests/test_rainviewer.py`. Exercita `servidor/rainviewer.py`.

- `test_buscar_frame_seleciona_frame_mais_recente_sem_usar_geracao_do_manifesto` — o frame é o mais recente, não a geração do manifesto.
- `test_buscar_frame_recusa_manifesto_sem_frame_ou_nao_confiavel` — manifesto sem frame ou não confiável é recusado.
- `test_buscar_tile_usa_host_fixo_e_valida_imagem` — o tile sai do host fixo e precisa ser PNG.
- `test_buscar_mascara_usa_endpoint_de_cobertura_fixo` — a máscara usa o endereço de cobertura fixo.
- `test_buscar_tile_recusa_frame_ou_coordenadas_invalidas` — frame ou coordenada inválida não gera pedido.
- `test_buscar_tile_recusa_resposta_remota_invalida` — resposta que não é imagem é recusada.
- `test_timeout_do_provedor_fica_indisponivel` — estouro de tempo fica indisponível.

Arquivo: `tests/test_openaip.py`. Exercita `servidor/openaip.py`.

- `test_buscar_tile_usa_host_fixo_header_secreto_e_cache_do_provedor` — host fixo, chave no cabeçalho e cache do provedor.
- `test_buscar_tile_falha_sem_chave_sem_chamar_provedor` — sem chave não há chamada.
- `test_buscar_tile_recusa_coordenadas_invalidas` — coordenada inválida não sai.
- `test_buscar_tile_rejeita_resposta_remota_invalida` — resposta inválida é rejeitada.
- `test_buscar_tile_converte_timeout_em_indisponibilidade` — timeout vira indisponível.

Arquivo: `tests/test_catalogo_aerodromos.py`. Exercita `servidor/catalogo.py`, `servidor/rotaer_aisweb.py` e `servidor/rotaer_parse.py`.

- `test_lista_so_aerodromo_e_rejeita_heliponto` — a lista oferecida é de aeródromo de avião.
- `test_download_rotaer_usa_endpoint_aisweb_confirmado` — a carga usa o endereço AISWEB previsto.
- `test_nascer_e_por_do_sol_usa_endpoint_aisweb_confirmado` — nascer e pôr do sol usam o endereço AISWEB previsto.
- `test_sol_aisweb_incompleto_ou_fora_de_utc_fica_indisponivel` — sol incompleto ou sem UTC fica indisponível.
- `test_emenda_ausente_nao_cria_coordenada` — sem emenda não nasce coordenada estimada.
- `test_download_rotaer_interpreta_lista_atual_e_pagina_por_quantidade` — a lista atual é lida em páginas.
- `test_download_rotaer_rejeita_total_alterado_durante_paginacao` — total que muda no meio invalida a carga.
- `test_download_rotaer_rejeita_pagina_vazia_antes_do_total` — página vazia antes do fim invalida a carga.
- `test_download_rotaer_reutiliza_detalhe_quando_versao_nao_muda` — detalhe da mesma versão não é baixado de novo.
- `test_download_rotaer_faz_fallback_para_html_sem_icao_correspondente` — XML sem o ICAO pedido tenta o HTML oficial.
- `test_carregar_rotaer_atualiza_e_limpa_contatos_da_emenda` — contatos novos entram e os que saíram da emenda são limpos.
- `test_carregar_rotaer_busca_contatos_para_cache_antigo` — cache antigo sem contato busca o detalhe.
- `test_carregar_rotaer_reutiliza_cache_persistido_e_invalida_versao` — cache persistido vale até a versão mudar.
- `test_download_rotaer_rejeita_detalhe_sem_elevacao` — detalhe sem elevação não entra.
- `test_download_rotaer_rejeita_coordenada_fora_do_intervalo` — latitude ou longitude fora do intervalo é rejeitada.
- `test_falha_em_detalhe_nao_publica_catalogo_parcial` — uma falha no detalhe não publica catálogo pela metade.

Arquivo: `tests/test_catalogo_aeronaves.py`. Exercita `servidor/catalogo_rab.py` e `servidor/proveniencia.py`.

- `test_ordem_pela_frota_e_exclui_aviao_grande` — a ordem segue a frota e o avião grande fica de fora.
- `test_recusa_modelo_sem_manual` — modelo sem dados técnicos completos não é oferecido.
- `test_oferece_apenas_trinta_modelos_completos_e_desempata_por_nome` — no máximo 30 completos, com desempate pelo nome.
- `test_carregar_rab_nao_associa_manual_sem_nome_exato` — o manual só liga ao nome exato.
- `test_carregar_rab_preserva_valores_de_registro_inelegivel` — registro que não entra na lista não perde o valor já gravado.
- `test_rab_indisponivel_nao_oferece_modelos_locais` — RAB indisponível não oferece modelo factual local.
- `test_fonte_mais_recente_e_empate_sem_selecao` — a fonte mais recente vence; empate não escolhe sozinho.

## Perfis sintéticos, proveniência e fotos

Arquivo: `tests/test_perfis_sinteticos.py`. Exercita `servidor/perfis_sinteticos.py` e a seleção.

- `test_perfis_sinteticos_aparecem_separados_sem_rab` — os sintéticos aparecem em categoria própria, sem RAB.

Arquivo: `tests/test_proveniencia.py`. Exercita `servidor/proveniencia.py`.

- `test_proxies_nao_dependem_de_intervalos_ou_referencias_aeronauticas` — o perfil sintético não depende de intervalo ou referência aeronáutica inventada.

Arquivo: `tests/test_importar_perfis_sinteticos.py`. Exercita `servidor/importar_perfis_sinteticos.py` com duas sessões SQLite em memória.

- `test_importa_vinte_perfis_sem_alterar_origem_ou_catalogos_do_destino` — copia os vinte perfis e não mexe na origem nem no catálogo do destino.
- `test_importa_esquema_legado_por_ordem_sem_alterar_origem` — lê o esquema legado na ordem e não altera a origem.
- `test_fonte_duplicada_no_esquema_legado_aborta_sem_escrever` — fonte duplicada aborta sem gravar.
- `test_importacao_repetida_nao_duplica_ou_altera_perfis` — repetir a importação não duplica.
- `test_origem_incompleta_aborta_sem_escrever_no_destino` — origem incompleta não escreve no destino.
- `test_fonte_tecnica_ausente_aborta_sem_escrever_no_destino` — fonte técnica ausente aborta sem escrever.
- `test_conflito_divergente_aborta_sem_insercoes_parciais` — valor divergente aborta sem inserção parcial.
- `test_comando_recusa_a_mesma_base_antes_de_conectar` — origem e destino iguais são recusados antes de conectar.

Arquivo: `tests/test_imagens_aeronave.py`. Exercita `servidor/imagens_aeronave.py` e `static/aeronaves/`.

- `test_cada_modelo_listado_tem_a_foto_da_familia` — cada modelo da regra recebe a foto da própria família.
- `test_modelo_sem_foto_conhecida_nao_recebe_imagem_de_outro` — modelo desconhecido não herda foto de outro.

Arquivo: `tests/test_migracao_aeronaves.py` e `tests/test_migracao_fonte_sintetica.py`. Exercitam as migrações Alembic de fonte.

- `test_migracao_invalida_fontes_nao_oficiais_sem_apagar_valores` — fonte não oficial deixa de valer e o valor numérico permanece.
- `test_migracao_adiciona_metadados_sinteticos_sem_alterar_fontes_existentes` — metadados sintéticos entram sem reescrever fontes já válidas.
- `test_migracao_permita_sintetica_sem_data_editorial` — fonte sintética pode existir sem data editorial.
- `test_migracao_nao_permite_reverter_com_dados_sinteticos` — a migração não volta atrás enquanto houver dado sintético.

## PDF

Arquivo: `tests/test_pdf.py`. Exercita `servidor/pdf_plano.py` e a rota `/planos/<id>/pdf`.

- `test_checklist_e_pdf` — o checklist marca item e o PDF abre com o nome `SBJD-SBAU-01-12-2026.pdf` e o aviso de que não autoriza o voo.

Arquivo: `tests/test_rota_pdf.py`. Exercita capa, fontes, programação e perfil sintético no PDF.

- `test_html_e_pdf_trazem_trecho_reabastecimento_e_aviso` — HTML e PDF trazem a escala, a hipótese de reabastecimento e o aviso.
- `test_pdf_de_plano_de_outro_piloto_e_recusado` — PDF de plano alheio é recusado.
- `test_capa_pdf_identifica_piloto_rota_data_e_emblema` — a capa traz o nome do piloto, a rota, a data e o emblema.
- `test_pdf_apresenta_apendice_de_fontes_e_so_contatos_verificados` — o apêndice lista as fontes e só publica telefone e e-mail verificados.
- `test_pdf_apresenta_programacao_utc_por_trecho_e_pernoite` — o PDF mostra os horários UTC legíveis e o pernoite.
- `test_pdf_identifica_fonte_e_validade_do_taf_redemet` — TAF da REDEMET leva fonte e validade.
- `test_perfil_sintetico_preserva_rotulo_no_resultado_e_no_pdf` — o aviso didático do perfil sintético permanece no PDF.

## Ambiente e operação

Arquivo: `tests/test_ambiente.py`. Exercita `servidor/ambiente.py` e o Alembic.

- `test_ambiente_ignora_variaveis_legadas_de_demo` — variável antiga de demonstração não escolhe o banco.
- `test_ambiente_recusa_url_de_produto_ausente_ou_invalida` — URL ausente, inválida ou que não é PostgreSQL é recusada.
- `test_criar_app_valida_url_antes_de_configurar_banco` — a aplicação valida a URL antes de ligar o banco.
- `test_criar_app_usa_database_url_com_variaveis_legadas_presentes` — com variável legada presente, vale `DATABASE_URL`.
- `test_alembic_usa_database_url_com_variaveis_legadas_presentes` — o Alembic usa a mesma `DATABASE_URL`.
- `test_conftest_aponta_banco_de_sessao_para_database_url_teste` — a sessão de teste aponta para `DATABASE_URL_TESTE`.

Arquivo: `tests/test_env.py`. Exercita `servidor/__init__.py`.

- `test_carregar_env_le_credenciais_aisweb_fora_do_repositorio` — a chave AISWEB é lida de um arquivo fora do repositório, com permissão restrita.

Arquivo: `tests/test_operacao_doc.py`. Lê `documentacao/operacao.md`.

- `test_operacao_nao_tem_segredo_e_cita_comandos` — o manual de operação não contém segredo e cita os comandos de subida.

## Revisão estática

Executada em seguida, com `radon` 6.0.1 e `mutmut` 3.8.1. Os limites estão em `pyproject.toml`.

### Cobertura

```bash
.venv-run/bin/pytest tests --ignore=tests/review -q --tb=line --cov=servidor --cov-report=term-missing:skip-covered
```

A meta de 27% foi atingida: **86,29%** de `servidor/` (3559 comandos, 488 sem passar). O pytest terminou com código 1 por causa das mesmas 5 falhas do produto, não por falta de cobertura. Quatro módulos ficaram em 100% e saíram da lista resumida: `ambiente.py`, `imagens_aeronave.py`, `openaip.py` e `perfis_sinteticos.py`.

| Módulo | Cobertura |
| --- | --- |
| `modelos.py` | 99% |
| `auth.py` | 95% |
| `pdf_layout.py` | 94% |
| `calculo.py` | 93% |
| `rota.py` | 92% |
| `planos_consulta.py` | 91% |
| `proveniencia.py` | 91% |
| `rainviewer.py` | 88% |
| `rotaer_parse.py` | 87% |
| `tempo.py` | 87% |
| `planos.py` | 86% |
| `__init__.py` | 86% |
| `rotaer_aisweb.py` | 85% |
| `pdf_visuais.py` | 84% |
| `pdf_plano.py` | 83% |
| `importar_perfis_sinteticos.py` | 79% |
| `catalogo.py` | 76% |
| `programacao.py` | 75% |
| `semente.py` | 61% |
| `catalogo_rab.py` | 58% |

### Tamanho

`tests/review/test_module_shape.py::test_modules_stay_within_size` **falhou**. O limite é 462 linhas.

| Módulo | Linhas |
| --- | --- |
| `servidor/tempo.py` | 1235 |
| `servidor/pdf_plano.py` | 557 |
| `servidor/pdf_layout.py` | 493 |
| `servidor/planos.py` | 489 |

### Complexidade

`test_modules_stay_within_complexity` está marcado com `pytest.mark.skip`, então a coleta do pytest não executa o corpo. O corpo foi chamado direto, com `radon` e o limite 23 de `pyproject.toml`. **Falhou.** Sete funções passam do limite:

| Função | Complexidade |
| --- | --- |
| `servidor/pdf_plano.py::_conteudo_relatorio` | 62 |
| `servidor/planos_consulta.py::construir_fontes_relatorio` | 54 |
| `servidor/tempo.py::_traduzir_token_fenomeno` | 31 |
| `servidor/tempo.py::satelite` | 28 |
| `servidor/tempo.py::carta` | 28 |
| `servidor/pdf_plano.py::_linhas_trecho` | 25 |
| `servidor/tempo.py::linhas_boletim` | 24 |

### Dependências

`tests/review/test_dependencies.py::test_imports_have_no_new_cycles` **falhou**. Ciclo novo: `servidor.pdf_plano` importa `servidor.planos`, e `servidor.planos` importa `servidor.pdf_plano`.

### Mutação

`tests/review/test_mutation.py::test_mutation_score` **falhou** em 43 s. O `mutmut` alterou um arquivo e gerou 700 mutantes. O teste exige zero mutantes sem teste e escore de pelo menos 56%.

| Resultado | Quantidade |
| --- | --- |
| Mortos pelos testes | 370 |
| Sobreviveram | 178 |
| Sem teste associado | 152 |
| Total | 700 |

O escore pela conta do teste, mortos sobre o total, é 52,9%. A barreira que interrompeu a verificação foi a de 152 mutantes sem teste.

## Diagnóstico

O aplicativo está sólido no que o piloto usa. A suíte fica vermelha por descompasso de testes e por limites de estrutura. Cálculo, sessão e isolamento não quebraram.

De 214 testes do produto, 209 passaram. Acesso, bloqueio, sessão de 8 horas, isolamento entre pilotos, rota, programação, catálogo, perfis sintéticos e a maior parte do PDF passaram. A cobertura de `servidor/` é 86,29%, acima da meta de 27%.

As cinco falhas se agrupam em três descompassos:

- A tela mudou e o teste não. O resumo é `<header id="resumo">`; o teste ainda procura `<section id="resumo">`. O texto «Informe de onde sai» saiu da página do plano e o teste de orientação ainda o exige.
- O TAF da REDEMET passou a ser consultado antes do Aviation Weather Center. O boletim chega, mas a lista de chamadas ganhou um `taf` a mais em dois testes.
- O PDF mostra o boletim novo na página e não reproduz, contínuo, o METAR gravado `METAR SBJD 121200Z 18010KT`. Essa é a única falha que pode ser de apresentação, não só de teste desatualizado.

A estrutura é o ponto fraco. Quatro módulos passam de 462 linhas, com `tempo.py` em 1235. Sete funções passam da complexidade 23; `_conteudo_relatorio` está em 62. `pdf_plano.py` e `planos.py` se importam em ciclo. A mutação de `calculo.py` ficou em 52,9%, abaixo de 56%: 370 mutantes mortos, 178 sobreviveram e 152 não têm teste. A cobertura de linha desse módulo é 93%, então o arquivo é executado, mas vários erros pequenos passariam sem o teste perceber.

Os módulos com menos cobertura são `catalogo_rab.py` (58%), `semente.py` (61%) e `programacao.py` (75%). São carga de dados e agenda, não o núcleo do voo.
