# Trabalho Prático - Shape Interpolation
Renato Sérgio Lopes Júnior
2016006875
===

## Implementação
O programa foi implementado com base no tutorial disponibilizado (http://tfc.duke.free.fr/old/models/md2.htm).

Algumas mudanças foram necessárias devido ao fato do tutorial estar em C++ e este programa ser desenvolvido em Python.

Para ler o arquivo binário, foram usados pacotes struct e ctype.

Foi usada a implementação do **Phong Shader** do Trabalho Prático 1.

A classe CMD2Model contém todas as informações obtidas do arquivo do modelo md2, como os vértices e os comandos OpenGL. Ela foi implementada tendo como base o tutorial já citado.

No main, o arquivo do modelo é carregado e são inicializadas a janela e as matrizes de transformação, além dos parâmetros de iluminação.

## Execução
Para executar o programa, basta rodar o seguinte comando em um Terminal:

    python tp3.py FILENAME

Onde FILENAME é o nome do arquivo md2 com o modelo a ser exibido.

O parâmetro opcional animation pode ser usado para especificar qual animação será exibida:

    python tp3.py FILENAME --animation 10

Quando o programa estiver executando, pode-se usar as setas da direita/esquerda do teclado para navegar pelas animações do modelo.
