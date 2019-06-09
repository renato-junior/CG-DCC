# Trabalho Prático - Ray Tracing
Renato Sérgio Lopes Júnior
2016006875
===

## Implementação
Neste trabalho foi produzido um programa que realiza a renderização por ray tracing de uma cena, seguindo como guia o livro "Ray Tracing in One Weekend", de Peter Shirley.

O programa possui as seguintes classes:

  - vec3: representação de um vetor com 3 dimensões.
  - ray: representação de um raio.
  - hit_record: classe que armazena informações sobre um hit, como o ponto onde ocorreu a colisão do raio com a superfície, o material, a normal, entre outras.
  - hitable: classe base para os objetos da cena que podem ser atingidos por um raio.
  - hitable_list: classe que armazena uma lista de objetos "hitable".
  - sphere: representa uma esfera.
  - moving_sphere: representa uma esfera com movimento (motion blur).
  - xy_rect, xz_rect, yz_rect: classes que representam retângulos nos planos xy, xz e yz, respectivamente.
  - flip_normals: classe auxiliar que inverte as normais de um objeto.
  - box: classe que representa uma caixa (paralelepípedo).
  - camera: representação da câmera que captura a cena.
  - material: classe base para criação de materiais.
  - lambertian: representação de um material lambertiano (difuso).
  - metal: representação de um material metálico.
  - dieletric: representação de um dielétrico (vidro).

Além disso, o programa possui os seguintes métodos auxiliares:

  - random_in_unit_disk: retorna uma posição aleatória em um disco unitário.
  - random_in_unit_sphere: retorna uma posição em uma esfera unitária.
  - refract: retorna o raio refratado.
  - schlick: aproximação para o material dielétrico.
  - color: retorna a cor final de um dado raio.
  - random_scene: cria uma cena aleatória.
  - create_ppm_file: cria uma arquivo de imagem PPM e inicializa o cabeçalho.
  - write_ppm: gera a imagem de uma dada cena e a escreve em um arquivo PPM.
  - process_multicore: renderiza a cena usando vários cores.
  - run_sub_image: renderiza uma subimagem.

Todos os pontos solicitados foram implementados, exceto o ray tracing distribuído para geração de sombras suaves.

## Execução

Para executar o código, basta entrar com o seguinte comando em um Terminal:

  python tp2.py IMAGENAME.ppm

Os parâmetros que podem ser definidos são apresentados a seguir:

  usage: tp2.py [-h] [--width WIDTH] [--height HEIGHT] [--rays RAYS]
                [--multicore]
                filename
  
  Ray Tracer.
  
  positional arguments:
    filename         Name of output file. (e.g. img.ppm)
  
  optional arguments:
    -h, --help       show this help message and exit
    --width WIDTH    The width of the generated image.
    --height HEIGHT  The height of the generated image.
    --rays RAYS      The number of rays to be cast per pixel.
    --multicore      Run the algorithm on multiple cores. If false, the
                     algorithm will run on a single core.

Os valores padrões dos parâmetros são:
  - width: 480
  - height: 340
  - rays: 10
  - multicore: False

Exemplos de execução

Renderizar cena usando 10 raios por pixel e gerar uma imagem 200x100 usando apenas um core:

  python tp2.py img.ppm --width 200 --height 100 --rays 10 

Renderizar cena usando 10 raios por pixel e gerar uma imagem 200x100 usando vários cores:

  python tp2.py img.ppm --width 200 --height 100 --rays 10 --multicore

