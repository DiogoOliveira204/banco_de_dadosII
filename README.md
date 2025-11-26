🏛 Museu Virtual – Banco de Dados
📘 Sobre o Projeto

Projeto da disciplina Banco de Dados II, com o objetivo de criar e manipular dados relacionais e não relacionais utilizando MySQL Workbench e MongoDB.

O sistema representa um Museu Virtual, onde são cadastradas obras de arte em diferentes formatos (imagens, vídeos, áudios e documentos).

👥 Integrantes

Ana Lívia

Bryan

Diogo

Emily

🧰 Tecnologias Utilizadas

MySQL Workbench – Banco relacional

MongoDB – Banco não relacional

Python – Geração automática de dados com Faker

Faker e mysql-connector-python – Bibliotecas auxiliares

🎯 Funcionalidades

Cadastro e autenticação de usuários

Cadastro e edição de obras e artistas

Associação entre obras, autores, estilos e exposições

Inserção e visualização de mídias (imagem, vídeo, áudio, documento)

Avaliação e favoritos de obras

⚙️ Execução

Clonar o repositório

Criar um ambiente virtual e instalar dependências:

pip install -r requirements.txt


Executar o script de população do banco:

python populate_museudb.py

🔄 Mudanças Implementadas no Projeto

🧩 Stored Procedures
sp_criar_usuario

Cadastro de novos usuários no sistema.

sp_gerenciar_obra

Realiza operações INSERT, UPDATE e DELETE sobre obras cadastradas.

sp_upload_midia

Responsável por atribuir mídias às obras.

⚡ Triggers
trg_log_avaliacao

Executada automaticamente após inserir um novo registro na tabela avaliacao, registrando o evento.

trg_log_favorito

Dispara sempre que um usuário marca uma obra como favorita, criando o respectivo log.

trg_prevent_duplicate_obra

Executada antes da inserção de uma obra.
Valida se já existe no banco outra obra com mesmo título e mesmo ano de criação, evitando duplicidade.

trg_prevent_duplicate_email

Executada antes de inserir um novo usuário.
Verifica se já existe um registro com o mesmo e-mail, garantindo unicidade.

👁 Views
vw_multimidia_obras

Exibe todas as mídias associadas às obras cadastradas.
Realiza JOIN entre Obras e Mídias.

vw_artistas_com_obras

Lista cada artista com suas respectivas obras.
Realiza JOIN entre obra_has_autor, obra e autor.

vw_obras_detalhes

Fornece uma visão completa e detalhada de cada obra, incluindo:
autor, estilos, tipos e associações.
Faz JOIN entre as tabelas:

autor

obra

estilo

tipo

estilo_has_tipo

obra_has_estilo

obra_has_autor

🗄 Banco de Dados NoSQL (MongoDB)

O MongoDB foi projetado para expandir as capacidades do Museu Virtual, armazenando dados dinâmicos e semiestruturados que não são ideais em um modelo relacional.

📚 Coleções Criadas
Coleção	Finalidade Principal
multimidia_obras	Armazena informações multimídia das obras (imagens, vídeos, arquivos) com metadados flexíveis.
logs_navegacao	Registra o comportamento dos usuários dentro do museu (cliques, buscas, visualizações).
recomendacoes_usuarios	Armazena recomendações personalizadas com base nos interesses de cada usuário (por estilo, tipo e histórico).

📚 Objetivo



Demonstrar a integração entre bancos relacionais e não relacionais, aplicando conceitos de modelagem, normalização e manipulação de dados em um contexto realista.
