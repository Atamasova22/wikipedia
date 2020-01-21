#!/usr/bin/env python
# coding: utf-8

# In[1]:


import re
import requests
import bs4

V = {}            
set_versh1 = set()  
set_versh2 = set() 
Vqueue1 = []    
Vqueue2 = []   
v1v2 = []
v2v1 = []
F1 = set()      
T1 = set()      
F2 = set()      
T2 = set()

def get_refs(ref:str):
    r = requests.get("https://en.wikipedia.org/wiki/"+ref)
    if r.status_code != 200: 
        return 'Error'
    soup = bs4.BeautifulSoup(r.text, features="lxml")
    cont = soup.findAll('div', attrs={'class':'mw-parser-output'})
    refs = []
    for div in cont:
        refs = refs + re.findall(r'href="/wiki/([^:]*?)"',str(div))
    return set(refs)

def random_page():
    r = requests.get("https://en.wikipedia.org/wiki/Special:Random")
    if r.status_code != 200: 
        return ''
    return r.url.split('/').pop()
 
def clear_versh():
    versh = {}
    versh['in'] = set() 
    versh['out'] = set()
    return versh

def add_versh_to_F(vname:str, F:set):
    global V
    
    vtoadd = set()
    newvtoadd = set([vname])
    
    contin = True
    while contin:
        contin = False
        vtoadd = newvtoadd
        newvtoadd = set()
        for name in vtoadd:
            if name not in F:
                versh = V.get(name)
                if versh!=None:
                    newvtoadd.update(versh['out'])
                    contin = True
                F.add(name)

def add_versh_to_T(vname:str, T:set):
    global V
    
    vtoadd = set()
    newvtoadd = set([vname])
    
    contin = True
    while contin:
        contin = False
        vtoadd = newvtoadd
        newvtoadd = set()
        for name in vtoadd:
            if name not in T:
                versh = V.get(name)
                if versh!=None:
                    newvtoadd.update(versh['in'])
                    contin = True  
                T.add(name)
        

def vunion(number):
    global set_versh1
    global set_versh2
    global Vqueue1
    global Vqueue2
    global F1
    global T1
    global F2
    global T2
    global V
    global v1
    global v2
    
    if number==1:
        oneset = set_versh1
        twoset = set_versh2
        onequeue = Vqueue1
        twoqueue = Vqueue2
        oneF = F1
        oneT = T1
        twoF = F2
        twoT = T2
        onev = v1
        twov = v2
    else:
        oneset = set_versh2
        twoset = set_versh1
        onequeue = Vqueue2
        twoqueue = Vqueue1
        oneF = F2
        oneT = T2
        twoF = F1
        twoT = T1
        onev = v2
        twov = v1
    
    name = ''
    while len(onequeue)>0 and len(name)==0:
        name = onequeue.pop(0)   
        if name not in oneset:
            name = ''
           
    if len(name)==0:        
        return 0
    
    print(name)
    
    oneversh = V.get(name)
    if oneversh == None:       
        oneversh = clear_versh()
        V[name] = oneversh
        
    outnames = set()
    outnames = get_refs(name) 
    oneversh['out'] = outnames              
    inoneT = False
    intwoT = False
    for oname in outnames:
        overtx = V.get(oname)       
        if overtx == None:
            overtx = clear_versh()
            V[oname] = overtx
            oneset.add(oname)
            onequeue.append(oname)
        overtx['in'].add(name)      
       
        if oname == onev or oname in oneT:
            inoneT = True  
      
        if oname == twov or oname in twoT:
            intwoT = True           
    
   
    for oname in outnames:
        add_versh_to_F(oname,oneF)   
    oneset.discard(name)
    if name in twoF:
        for oname in outnames:
            add_versh_to_F(oname,twoF)
    twoset.discard(name)
    
   
    if inoneT:
        add_versh_to_T(name,oneT)
    if intwoT:
        add_versh_to_T(name,twoT)
        
def find_path(FTset:set, vf:str, vt:str):
    global V
    
    lengths = {}
    FTset.add(vf)
    FTset.add(vt)
    lengths[-1] = set(FTset)
    lengths[0] = set()
    lengths[0].add(vf)
    lengths[-1].discard(vf)
    i=1
    notfinished = True
    while len(lengths[-1]) and notfinished and i<50:
        lengths[i] = set()
        for vn in lengths[i-1]:
            versh = V[vn]
            for vnn in versh['out']:
                if vnn in lengths[-1]:
                    lengths[i].add(vnn)
                    lengths[-1].discard(vnn)
                    if vnn == vt:
                        notfinished = False
        i+=1
    
    path = [vt]
    for j in range(2,i):
        versh = V[path[0]]
        path.insert(0,(versh['in']&lengths[i-j]).pop())
    path.insert(0,vf)
    return path
    

if __name__ == '__main__':

    v1 = random_page()
    v2 = random_page()
    print("From: " + str(v1))
    print("To: " + str(v2))
    
    if len(set_versh1)==0:
        Vqueue1 = [v1]
        set_versh1 = set(Vqueue1)
    if len(set_versh2)==0:
        Vqueue2 = [v2]
        set_versh2 = set(Vqueue2)
        
    f = open('text.txt', 'w')
  
    for i in range(1000):
        vunion(1)
        vunion(2)

        if len(v1v2) == 0:
            if len(F1&T2):
                v1v2 = find_path(F1&T2, v1, v2)
            
        if len(v2v1) == 0:
            if len(F2&T1):
                v2v1 = find_path(F2&T1, v2, v1)
                
        print("iter "+str(i))
        print("\n")
        
        

        if len(v1v2)>0 and len(v2v1)>0:
            f.write(v1 + "->" + v2 + "len: " + str(len(v1v2)-1) + " path: " + str(v1v2) + 
                   "\n" + v2 + "->" + v1 + "len: "  + str(len(v2v1)-1) + " path: " + str(v2v1) + '\n')
            
            print("page1 -> page2 steps: " + str(len(v1v2)-1) + " path: " + str(v1v2))
            print("\npage2 -> page1 steps: " + str(len(v2v1)-1) + " path: " + str(v2v1))
    
            break
    f.close()


# In[ ]:




