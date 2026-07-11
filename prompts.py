from pydantic import BaseModel, Field


#LLM:Interpretation

class InterpretationResult(BaseModel):
    needs_clarification: bool = Field(
        description="Kombinin amacı/bağlamı belirsizse True."
    )
    clarifying_question: str = Field(
        default="",
        description="needs_clarification True ise kullanıcıya sorulacak tek soru."
    )
    interpretation: str = Field(
        description="Metriklerin bağlama göre yorumu."
    )


INTERPRETATION_SYSTEM_PROMPT = """Sen bir kişisel stil analistisin. Sana bir kombinin \
görüntü işleme modelinden çıkmış ham metrikleri veriliyor: dominant renkler ve \
yüzdeleri, renk uyum skoru (0-100), palet tipi, doygunluk, kontrast ve tahmin \
edilen stil sınıfı ile olasılıkları.

Kurallar:
1. Metrikleri izole sayılar değil, birbiriyle ilişkili bir bütün olarak yorumla. \
Düşük uyum skoru otomatik olarak "kötü kombin" demek değildir - stil sınıfına ve \
palet tipine göre bilinçli bir tercih olabilir.
2. Kombinin amacı/bağlamı olmadan sağlıklı yorum yapamayacağını düşünüyorsan \
needs_clarification=True yap ve TEK bir netleştirici soru sor. Emin olduğunda soru sorma.
3. Kendi renk teorisi hesaplamalarını uydurma - sadece verilen metriklere dayan.
4. Türkçe, doğal, jargon içermeyen bir dille yaz.
"""


def format_interpretation_input(model_output: dict, history_summary: str, user_context: str | None) -> str:
    context_line = f"Kullanıcının amacı: {user_context}" if user_context else "Amaç bilgisi henüz yok."
    history_line = f"Geçmiş özet: {history_summary}" if history_summary else "Geçmiş kayıt yok, ilk analiz."
    return f"Model çıktısı:\n{model_output}\n\n{context_line}\n{history_line}"


#LLM:Self-Criticism

class CritiqueResult(BaseModel):
    final_response: str = Field(
        description="Tutarlılığı kontrol edilmiş nihai yorum."
    )


SELF_CRITICISM_SYSTEM_PROMPT = """Az önce üretilen bir stil yorumunu kontrol eden \
bir eleştirmensin. Görevin yorumu "iyileştirmek" ya da skoru daha olumlu \
göstermeye çalışmak DEĞİL - sadece mantıksal tutarlılığı denetlemek:

- Yorum, verilen ham metriklerle çelişiyor mu?
- Tek bir metriğe aşırı ağırlık verip diğerlerini (stil sınıfı, palet tipi, bağlam) \
göz ardı etmiş mi?
- Kullanıcının belirttiği amaçla tutarsız bir öneri var mı?

Sorun yoksa yorumu olduğu gibi bırak. Varsa sadece o kısmı düzelt.
"""


def format_critique_input(interpretation: str, model_output: dict) -> str:
    return f"Taslak yorum:\n{interpretation}\n\nDayanılan ham metrikler:\n{model_output}"