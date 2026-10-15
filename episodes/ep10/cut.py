# Découpe ép.10 ; index = ordre de la vidéo ; noms lus à voix haute par Gemini retirés
import librosa, numpy as np, wave, json, glob
F={k:glob.glob(f'rec/*{k}.wav')[0] for k in ('12_44PM','12_47PM','12_50PM','12_52PM','2_11PM','2_12PM','3_05PM','3_03PM')}
A,MI,FV,B='12_44PM','12_47PM','12_50PM','12_52PM'
X=[('MIMI',MI,0,2.4,"Tantie Awa, goûtez un peu."),('AWA',A,1.1,5.3,"Hmm… Elles sont très bonnes. Tu as acheté ça où ?"),
('MIMI',MI,2.7,6.12,"Chez Bakary, Tantie. Ils font de bonnes brochettes, maintenant."),('AWA',A,5.6,8.4,"Beurk !"),
('AWA',A,8.6,11.4,"Pourtant… ce n'était pas mal."),('AWA',A,11.7,15.7,"Non. Ces idiots de V.D.B. ne peuvent rien faire de bon."),
('AWA',A,15.8,23.9,"Fatim. Tiens deux mille francs. Je commande des brochettes à ton nom. Tu les reçois, et tu me les donnes."),
('FATIM',FV,16.8,20.25,"Pas de problème, Awa. Mais pourquoi à mon nom ?"),('AWA',A,24.2,25.3,"Ne pose pas de questions."),
('BAKARY',B,0,3.0,"Hmm hmm hmm…"),('BAKARY',B,3.0,8.3,"Bonsoir, ma sœur ! Livraison Sounsouni, Chez Bakary. Six brochettes pour Fatim."),
('FATIM',FV,21.2,23.4,"C'est moi, Fatim. Tenez."),('BAKARY',B,8.9,16.2,"Aïe… Je n'ai pas la monnaie sur moi. J'ai une autre livraison à trois cents mètres. Je reviens tout de suite avec tes cinq cents."),
('FATIM',FV,23.9,25.3,"Prenez votre temps…"),('FATIM',FV,26.6,29.2,"Voilà tes brochettes, Awa. Et ta monnaie."),
('FATIM_P',FV,33.1,36.8,"Je rembourse Awa… et j'attendrai les cinq cents du beau livreur."),('AWA',A,27.2,30.6,"Hmm… Il est parti. Personne ne saura."),
('BAKARY',B,17.0,19.4,"Fatim, voilà ta…"),('BAKARY',B,20.1,24.3,"Ma déesse ! Comment tu vas ? Qu'est-ce que tu fais là ?"),
('BAKARY',B,25.4,28.1,"Alors… tu m'invites ?"),('AWA',A,30.9,35.0,"T'inviter ? Mais tu te crois où, toi ?"),
('BAKARY',B,28.1,31.6,"Non, non, non, non ! Ne t'énerve pas, surtout. Ce n'était pas pour t'énerver."),
('BAKARY',B,32.3,39.2,"Ah, mais… ce sont mes brochettes, ça ! Mes nouvelles brochettes ! Elles sont comment ?"),
('BAKARY',B,39.3,43.2,"Si je savais que tu étais chez Fatim, je t'en aurais fait beaucoup, en cadeau."),
('AWA',A,35.0,38.6,"Tes brochettes ? Je ne savais même pas qu'elles venaient de chez toi."),('AWA',A,38.9,43.9,"Et elles ne sont pas bonnes du tout. Trop dures. Trop salées."),
('FATIM',FV,38.9,42.1,"Bakary ! Tu es revenu pour la monnaie ? Donne-moi."),('FATIM',FV,42.3,43.0,"Merci."),
('FATIM',FV,43.1,48.7,"Awa, ta commande, elle est bonne, non ? Moi, je n'ai même pas goûté. Donne-m'en une, que je goûte."),
('AWA',A,44.3,45.48,"Tchiiip !"),('FATIM',FV,49.9,54.15,"Mais qu'est-ce qu'elle a ? Qu'est-ce qui s'est passé ? Tu la connais ?"),
('BAKARY',B,44.1,46.4,"Non, non… Ne t'en fais pas pour elle."),('BAKARY',B,46.8,50.9,"Bon, il est l'heure que je me casse. Il fait déjà tard."),
('FATIM',FV,55.1,57.5,"Bakary… Tu as mon numéro, maintenant…"),('BAKARY',B,51.1,53.84,"Ah oui ! Pour tes prochaines commandes !"),
('FATIM',FV,57.5,60.24,"Pour mes commandes… Hmm."),
('VOIX_OFF',FV,0,15.4,"Beignets, brochettes, crédit téléphonique : sur Sounsouni, chaque petit commerce a sa boutique, et ses clients commandent à toute heure. Téléchargez l'application sur sounsouni.pro, sur Android… et bientôt sur iPhone."),
('MIMI_P','2_11PM',0,7.0,"Il est déjà treize heures… J'ai un petit creux. Qu'est-ce que je vais manger ?"),
('MIMI_P','2_11PM',7.0,9.5,"Attends… je regarde sur Sounsouni."),
('MIMI_P','2_11PM',9.7,16.3,"Oh ! Des brochettes, chez Bakary ! Et les prix sont bons. Je commande !"),
('SEYDOU','2_12PM',0,3.04,"Livraison Sounsouni ! Trois brochettes pour Mimi."),
('MIMI','2_11PM',16.6,18.32,"Merci !"),
('FATIM','3_05PM',0.85,4.6,"Tout est OK, Awa. Voilà tes brochettes, et ta monnaie."),
('FATIM_P','3_05PM',4.7,7.28,"Il n'avait pas la monnaie… il va revenir avec mes cinq cents."),
('FATIM','3_05PM',7.3,8.32,"Je gère !"),
('AWA_P','3_03PM',0,5.7,"Hmm… J'ai encore envie de goûter les brochettes de cet après-midi…"),
('AWA_P','3_03PM',7.4,10.1,"Non. Je vais acheter autre chose."),
('AWA_P','3_03PM',13.0,16.3,"Mais… pourquoi pas essayer ?"),
('AWA_P','3_03PM',16.5,19.4,"Non, non. Autre chose."),
('AWA_P','3_03PM',20.4,29.9,"Attends… j'ai une idée ! Je vais demander à Fatim de commander pour moi. Comme ça, même si Bakary vient livrer, il ne me verra pas."),
('AWA','3_03PM',30.6,36.5,"Fatim ! J'étais loin, je n'ai pas entendu ce que vous avez dit. Tout est OK ?")]
L=[]
for i,(c,f,a,b,t) in enumerate(X):
    y,sr=librosa.load(F[f],sr=None,offset=a,duration=b-a)
    iv=[r for r in librosa.effects.split(y,top_db=32,frame_length=1024,hop_length=256) if (r[1]-r[0])/sr>0.05]
    y=y[max(0,iv[0][0]-int(0.04*sr)):iv[-1][1]+int(0.12*sr)]; y=y/np.abs(y).max()*0.9
    w=wave.open(f'vo/L{i:02d}.wav','wb'); w.setnchannels(1); w.setsampwidth(2); w.setframerate(sr); w.writeframes((y*32767).astype(np.int16).tobytes()); w.close()
    L.append([c,'normal',t,t])
json.dump(L,open('dialogue.json','w'),ensure_ascii=False,indent=0); print(len(L))
