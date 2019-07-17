from gensim import corpora,models,similarities
from model.common_model import *
import nltk

def conclude_similar():
    oss_info = OsslibMetedata.select()
    all_doc_list = []
    all_id_list = []
    for per_oss_info in oss_info:
        if per_oss_info.oss_description == None or per_oss_info.oss_description == '':
            continue
        doc_list = nltk.word_tokenize(per_oss_info.oss_description)
        all_doc_list.append(doc_list)
        all_id_list.append(per_oss_info.id)
    dictionary = corpora.Dictionary(all_doc_list)
    corpus = [dictionary.doc2bow(doc) for doc in all_doc_list]
    tfidf = models.TfidfModel(corpus)

    #oss_test_info = OsslibMetedata.get(4437)
    #doc_test_list = nltk.word_tokenize(oss_test_info.oss_description)
    #doc_test_vec = dictionary.doc2bow(doc_test_list)
    index = similarities.SparseMatrixSimilarity(tfidf[corpus], num_features=len(dictionary.keys()))
    i = 0
    for per_corpus in corpus:
        sim = index[tfidf[per_corpus]]
        #print()
        similar_id = all_id_list[sorted(enumerate(sim), key=lambda item: -item[1])[0][0]]
        if similar_id != all_id_list[i]:
            print(str(all_id_list[i]) + '-' + str(similar_id))
        i += 1