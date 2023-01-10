# import aiohttp
from fastai.vision.all import load_learner

girl_class = load_learner('ai/models/girl_classifier.pkl', cpu=True)
# async with aiohttp.ClientSession() as session:
#     async with session.get(url=url) as response:
#         if not response.ok:
#             pass
#         img = PILImage.create(await response.content.read())
# pred, pred_idx,probs = learn_inf.predict(img)
# f'Prediction: {pred}; Probability: {probs[pred_idx]:.04f}'
