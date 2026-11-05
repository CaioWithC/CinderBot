"""Quiz defaults and exact matching after harmless spelling normalization."""
import unicodedata

MIN_INTERVAL = 30 * 60
MAX_INTERVAL = 60 * 60
ACTIVITY_WINDOW = 10 * 60
MIN_MESSAGES = 5
MIN_PARTICIPANTS = 2
ROUND_SECONDS = 120
DEFAULT_REWARD = 1000

SEED_QUESTIONS = (
    # ── Ciência ──
    ("Qual é o elemento químico com o maior número atômico encontrado naturalmente na Terra?", ["Urânio", "Uranio"]),
    ("Qual vitamina o corpo humano produz quando exposto à luz solar?", ["Vitamina D"]),
    ("Quantos ossos tem o corpo humano adulto?", ["206"]),
    ("Qual é a partícula subatômica com carga negativa?", ["Elétron", "Eletron", "Electron"]),
    ("Qual é o gás mais abundante na atmosfera terrestre?", ["Nitrogênio", "Nitrogenio"]),
    ("Qual planeta do sistema solar possui a maior quantidade de luas conhecidas?", ["Saturno"]),
    ("Qual é o metal líquido à temperatura ambiente?", ["Mercúrio", "Mercurio"]),
    ("Qual cientista formulou a teoria da relatividade?", ["Albert Einstein", "Einstein"]),
    ("Qual é o menor osso do corpo humano?", ["Estribo"]),
    ("Qual é a fórmula química da água?", ["H2O"]),

    # ── Geografia ──
    ("Qual é o maior deserto do mundo?", ["Saara", "Sahara"]),
    ("Qual país tem a maior extensão territorial do mundo?", ["Rússia", "Russia"]),
    ("Qual é o rio mais longo do mundo?", ["Nilo", "Rio Nilo"]),
    ("Qual é o ponto mais profundo dos oceanos?", ["Fossa das Marianas"]),
    ("Qual é a capital da Mongólia?", ["Ulan Bator", "Ulaanbaatar"]),
    ("Qual é o menor país do mundo em área territorial?", ["Vaticano", "Cidade do Vaticano"]),
    ("Em qual continente fica o Djibuti?", ["África", "Africa"]),
    ("Qual país é conhecido como a Terra do Sol Nascente?", ["Japão", "Japao"]),
    ("Qual é a montanha mais alta do mundo?", ["Monte Everest", "Everest"]),
    ("Quantos fusos horários a Rússia possui?", ["11"]),

    # ── História ──
    ("Em que ano caiu o Muro de Berlim?", ["1989"]),
    ("Quem foi o primeiro imperador do Brasil?", ["Dom Pedro I", "Pedro I", "D. Pedro I"]),
    ("Em que ano foi proclamada a República no Brasil?", ["1889"]),
    ("Qual civilização construiu Machu Picchu?", ["Inca", "Incas"]),
    ("Qual foi a última dinastia imperial da China?", ["Qing"]),
    ("Em que ano ocorreu a Revolução Francesa?", ["1789"]),
    ("Quem pintou o teto da Capela Sistina?", ["Michelangelo", "Miguel Ângelo", "Miguel Angelo"]),
    ("Qual faraó egípcio teve a tumba descoberta quase intacta em 1922?", ["Tutancâmon", "Tutancamon", "Tutankamon", "Tutankhamon"]),
    ("Qual tratado encerrou a Primeira Guerra Mundial?", ["Tratado de Versalhes"]),
    ("Em que ano os Estados Unidos declararam independência?", ["1776"]),

    # ── Matemática e Lógica ──
    ("Quanto é a raiz quadrada de 1.444?", ["38"]),
    ("Qual é o único número primo par?", ["2"]),
    ("Quantas faces tem um icosaedro?", ["20"]),
    ("Qual é o valor de pi arredondado para duas casas decimais?", ["3,14", "3.14"]),
    ("Quanto é 17 elevado ao quadrado?", ["289"]),
    ("Qual é o próximo número primo depois de 97?", ["101"]),
    ("Qual é o resultado de fatorial de 6 (6!)?", ["720"]),
    ("Quantos graus tem a soma dos ângulos internos de um hexágono?", ["720"]),

    # ── Literatura e Língua Portuguesa ──
    ("Quem escreveu 'Dom Casmurro'?", ["Machado de Assis"]),
    ("Qual é a figura de linguagem que atribui características humanas a objetos ou animais?", ["Prosopopeia", "Personificação", "Personificacao", "Prosopopéia"]),
    ("Qual poeta português escreveu 'Os Lusíadas'?", ["Camões", "Camoes", "Luís de Camões", "Luis de Camoes"]),
    ("Quem escreveu 'O Pequeno Príncipe'?", ["Saint-Exupéry", "Saint-Exupery", "Antoine de Saint-Exupéry", "Antoine de Saint-Exupery"]),
    ("Qual é o maior livro da Bíblia em número de capítulos?", ["Salmos"]),
    ("Quem escreveu 'Grande Sertão: Veredas'?", ["Guimarães Rosa", "Guimaraes Rosa", "João Guimarães Rosa"]),

    # ── Cultura Pop e Entretenimento ──
    ("Qual é o nome do protagonista de 'The Legend of Zelda'?", ["Link"]),
    ("Em 'Death Note', qual é o nome verdadeiro do detetive L?", ["L Lawliet", "Lawliet"]),
    ("Qual estúdio de animação japonês produziu 'A Viagem de Chihiro'?", ["Studio Ghibli", "Ghibli"]),
    ("Qual é o nome do protagonista de 'Naruto' completo?", ["Naruto Uzumaki"]),
    ("Qual é o nome do Pikachu na Pokédex (número nacional)?", ["25"]),
    ("Em 'One Piece', qual é o nome da fruta que o Luffy comeu?", ["Gomu Gomu no Mi", "Gomu Gomu", "Hito Hito no Mi Modelo Nika"]),
    ("Qual é o nome do planeta natal de Goku em Dragon Ball?", ["Vegeta", "Planeta Vegeta"]),
    ("Quantos filmes compõem a saga principal de 'Star Wars'?", ["9"]),

    # ── Música ──
    ("Qual banda britânica lançou o álbum 'The Dark Side of the Moon'?", ["Pink Floyd"]),
    ("Qual compositor ficou surdo e ainda assim continuou compondo?", ["Beethoven", "Ludwig van Beethoven"]),
    ("Quantas cordas tem um violão padrão?", ["6", "seis"]),
    ("Qual grupo sul-coreano é conhecido por hits como 'Dynamite' e 'Butter'?", ["BTS"]),
    ("Qual cantora é conhecida por ser a mais jovem a ganhar um Grammy?", ["Billie Eilish"]),
    ("Qual é o nome da cantora que anteriormente era da Disney e lançou o álbum 'SOUR'?", ["Olivia Rodrigo"]),
    ("Qual artista é conhecida por ter um clipe numa bola de demolição gigante e por cantar 'Wrecking Ball'?", ["Miley Cyrus"]),

    # ── Miscelânea difícil ──
    ("Qual é o código de status HTTP que significa 'Não encontrado'?", ["404"]),
    ("Em que linguagem de programação o Linux foi originalmente escrito?", ["C"]),
    ("Qual é a moeda oficial do Japão?", ["Iene", "Yen"]),
    ("Quantos cromossomos tem uma célula humana normal?", ["46"]),
    ("Qual é o país com mais ganhadores do Prêmio Nobel?", ["Estados Unidos", "EUA"]),
    ("Qual instrumento musical tem 88 teclas?", ["Piano"]),
    ("Qual é o animal terrestre mais rápido do mundo?", ["Guepardo", "Chita"]),
    ("Qual é o símbolo químico do ouro?", ["Au"]),
    ("Qual país inventou o papel?", ["China"]),
    ("Qual é a unidade de medida de resistência elétrica?", ["Ohm"]),
)


def normalize_answer(value):
    value = unicodedata.normalize("NFKD", value.casefold())
    value = "".join(char for char in value if not unicodedata.combining(char))
    return " ".join(value.split()).strip(" .!?\"'“”‘’")


def suggestion_answers(answer, aliases=""):
    values = list(dict.fromkeys(text.strip() for text in [answer, *aliases.splitlines()] if text.strip()))
    if not values or len(values) > 10 or any(not normalize_answer(text) or len(text) > 100 for text in values):
        raise ValueError("Informe uma resposta válida e até 9 alternativas, uma por linha, com até 100 caracteres cada.")
    return values
