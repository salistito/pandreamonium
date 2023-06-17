
import string
import spacy
from spacy.lang.es import stop_words
import nltk
from nltk.corpus import stopwords
#nltk.download('stopwords')
#nltk.download('punkt')

custome_stop_words = [
    'algún','alguna','algunas','alguno','algunos','ambos','ampleamos','ante','antes','aquel','aquellas','aquellos','aqui','arriba','atras',
    'bajo','bastante','bien','cada','cierta','ciertas','cierto','ciertos','como','con','conseguimos','conseguir','consigo','consigue','consiguen','consigues','cual','cuando',
    'dentro','desde','donde','dos','el','ellas','ellos','empleais','emplean','emplear','empleas','empleo','en','encima','entonces','entre','era','eramos','eran','eras','eres','es','esta','estaba','estado','estais','estamos','estan','estoy',
    'fin','fue','fueron','fui','fuimos','gueno','ha','hace','haceis','hacemos','hacen','hacer','haces','hago','incluso','intenta','intentais','intentamos','intentan','intentar','intentas','intento','ir','la','largo','las','lo','los',
    'mientras','mio','modo','muchos','muy','nos','nosotros','otro','para','pero','podeis','podemos','poder','podria','podriais','podriamos','podrian','podrias','por','por','qué','porque','primero','puede','pueden','puedo',
    'quien','sabe','sabeis','sabemos','saben','saber','sabes','ser','si','siendo','sin','sobre','sois','solamente','solo','somos','soy','su','sus',
    'también','teneis','tenemos','tener','tengo','tiempo','tiene','tienen','todo','trabaja','trabajais','trabajamos','trabajan','trabajar','trabajas','trabajo','tras','tuyo',
    'ultimo','un','una','unas','uno','unos','usa','usais','usamos','usan','usar','usas','uso','va','vais','valor','vamos','van','vaya','verdad','verdadera','verdadero','vosotras','vosotros','voy',
    'yo','él','ésta','éstas','éste','éstos','última','últimas','último','últimos','a','añadió','aún','actualmente','adelante','además','afirmó','agregó','ahí','ahora','al','algo','alrededor','anterior','apenas','aproximadamente','aquí','así','aseguró','aunque','ayer',
    'buen','buena','buenas','bueno','buenos','cómo','casi','cerca','cinco','comentó','conocer','consideró','considera','contra','cosas','creo','cuales','cualquier','cuanto','cuatro','cuenta',
    'da','dado','dan','dar','de','debe','deben','debido','decir','dejó','del','demás','después','dice','dicen','dicho','dieron','diferente','diferentes','dijeron','dijo','dio','durante',
    'e','ejemplo','ella','ello','embargo','encuentra','esa','esas','ese','eso','esos','está','están','estaban','estar','estará','estas','este','esto','estos','estuvo','ex','existe','existen','explicó','expresó',
    'fuera','gran','grandes','había','habían','haber','habrá','hacerlo','hacia','haciendo','han','hasta','hay','haya','he','hecho','hemos','hicieron','hizo','hoy','hubo','igual','indicó','informó','junto','lado','le','les','llegó','lleva','llevar','luego','lugar',
    'más','manera','manifestó','mayor','me','mediante','mejor','mencionó','menos','mi','misma','mismas','mismo','mismos','momento','mucha','muchas','mucho',
    'nada','nadie','ni','ningún','ninguna','ningunas','ninguno','ningunos','no','nosotras','nuestra','nuestras','nuestro','nuestros','nueva','nuevas','nuevo','nuevos','nunca',
    'o','ocho','otra','otras','otros','parece','parte','partir','pasada','pasado','pesar','poca','pocas','poco','pocos','podrá','podrán','podría','podrían','poner','posible',
    'próximo','próximos','primer','primera','primeros','principalmente','propia','propias','propio','propios','pudo','pueda','pues',
    'qué','que','quedó','queremos','quién','quienes','quiere','realizó','realizado','realizar','respecto',
    'sí','sólo','se','señaló','sea','sean','según','segunda','segundo','seis','será','serán','sería','sido','siempre','siete','sigue','siguiente','sino','sola','solas','solos','son',
    'tal','tampoco','tan','tanto','tenía','tendrá','tendrán','tenga','tenido','tercera','toda','todas','todavía','todos','total','trata','través','tres','tuvo','usted','varias','varios','veces','ver','v','y','ya'
]

"""
consolidated_stop_words = cloud_nltk_stop_words = stopwords.words('spanish')
cloud_spacy_stop_words = list(stop_words.STOP_WORDS)
cloud_nltk_stop_words.extend(cloud_spacy_stop_words)
"""
consolidated_punctuation = string.punctuation+'¡'
consolidated_stop_words = custome_stop_words

es_nlp = spacy.load('es_core_news_lg')
#en_nlp = spacy.load('en_core_web_lg')