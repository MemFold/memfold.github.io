"""Render page-specific vector charts. Run with Python and matplotlib installed.
Data in figure-data.json is copied from the paper's plotting sources unchanged.
"""
import json
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

ROOT=Path(__file__).resolve().parents[1]
DATA=json.loads((Path(__file__).parent/'figure-data.json').read_text())
ACCENT='#2563b8'; INK='#242728'; MUTED='#666b70'; LINE='#e1e2df'; SECOND='#8b5c9d'
# Shared SVG text roles, in the figure's native point coordinates.
TYPE={'title':14,'label':12,'tick':11,'annotation':11,'legend':11,'eyebrow':10}
plt.rcParams.update({'font.family':'sans-serif','font.sans-serif':['Arial','DejaVu Sans'],
    'font.size':TYPE['label'],'text.color':INK,'axes.labelcolor':MUTED,'xtick.color':MUTED,
    'ytick.color':MUTED,'svg.fonttype':'none','svg.hashsalt':'memfold-web',
    'axes.facecolor':'none','figure.facecolor':'none','savefig.facecolor':'none'})


def style(ax):
    ax.spines[['top','right']].set_visible(False)
    for side in ['left','bottom']:
        ax.spines[side].set_color(LINE)
    ax.tick_params(axis='both',length=0,pad=7,labelsize=TYPE['tick'])
    ax.grid(axis='y',color=LINE,linewidth=.7)
    ax.set_axisbelow(True)


def save(fig,name,tight=True):
    fig.savefig(ROOT/'assets'/name,format='svg',bbox_inches='tight' if tight else None,pad_inches=.15,
        metadata={'Date':None,'Creator':'MemFold website figures'})
    plt.close(fig)
    output=ROOT/'assets'/name
    output.write_text('\n'.join(line.rstrip() for line in output.read_text().splitlines())+'\n')


def training(mobile=False):
    fig,axes=plt.subplots(2 if mobile else 1,1 if mobile else 2,
        figsize=(5.1,7.3) if mobile else (10.2,3.7))
    order=['GRPO','GRPO+OPD','SDPO','OPSD','MemFold']
    tones={'GRPO':'#87968d','GRPO+OPD':'#98a6aa','SDPO':'#b2b9b1','OPSD':'#b7aaa0','MemFold':ACCENT}
    for i,ax in enumerate(axes):
        style(ax)
        if mobile: ax.tick_params(labelsize=TYPE['tick'])
        ax.set_title('By optimizer updates' if i==0 else 'By student rollouts',loc='left',fontsize=TYPE['title'],fontweight='bold',pad=18)
        for name in order:
            values=DATA['training'][name]
            x=DATA['steps'] if i==0 else values['rollouts']
            y=values['accuracy'] if i==0 else values['rollout_accuracy']
            ours=name=='MemFold'
            ax.plot(x,y,color=tones[name],lw=2.4 if ours else 1.5,
                marker='o' if ours else None,ms=4,zorder=4 if ours else 2)
            offset={'SDPO':-.55,'GRPO+OPD':.55}
            if i==1: offset.update({'MemFold':.7,'GRPO':-.6})
            ax.annotate(name,xy=(x[-1],y[-1]),xytext=(390 if i==0 else 6300,y[-1]+offset.get(name,0)),
                va='center',fontsize=TYPE['annotation'],color=ACCENT if ours else MUTED,fontweight='bold' if ours else 'normal',annotation_clip=False)
        ax.set_ylabel('Accuracy (%)',fontsize=TYPE['label'],labelpad=10)
        ax.set_xlabel('Gradient update steps' if i==0 else 'Cumulative student rollouts',fontsize=TYPE['label'],labelpad=12)
        ax.set_xlim((-12,380) if i==0 else (-150,6150))
        ax.set_xticks([0,100,200,300,369] if i==0 else [0,2000,4000,6000])
        ax.set_ylim((45,72) if i==0 else (45,65))
        ax.set_yticks([50,60,70] if i==0 else [45,50,55,60,65])
    fig.subplots_adjust(left=.15 if mobile else .07,right=.76 if mobile else .88,
        bottom=.09 if mobile else .21,top=.94 if mobile else .87,
        wspace=.65,hspace=.65)
    save(fig,'training-efficiency-mobile.svg' if mobile else 'training-efficiency.svg')


def memory(reliance=False):
    fig,ax=plt.subplots(figsize=(5.1,4.15));style(ax);ax.tick_params(labelsize=TYPE['tick'])
    colors=[ACCENT,SECOND];markers=['o','s'];x=range(4)
    if reliance:
        ax.axvspan(-.35,.35,color='#f1f2ef',zorder=0)
    else:
        ax.axvspan(1.82,2.18,color='#f1f2ef',zorder=0)
    handles=[]
    for i,(name,data) in enumerate(DATA['memory'].items()):
        y=data['conditions' if reliance else 'accuracy']
        xx=[v+(-.1 if i==0 else .1) for v in x] if reliance else list(x)
        if reliance: ax.scatter(xx,y,s=48,marker=markers[i],color=colors[i],zorder=4)
        else: ax.plot(xx,y,marker=markers[i],ms=6,lw=2,color=colors[i],zorder=3)
        for xv,yv in zip(xx,y):
            ax.annotate(f'{yv:.1f}',(xv,yv),xytext=(0,-18 if reliance and i==0 else 10),
                textcoords='offset points',ha='center',fontsize=TYPE['annotation'],color=colors[i])
        handles.append(Line2D([],[],marker=markers[i],color=colors[i],lw=0 if reliance else 2,label=name.replace('PersonaMem-','')))
    ax.set_ylabel('Accuracy (%)',labelpad=10)
    if reliance:
        ax.set_xticks(list(x),['Matched','Shuffled','Null','Text teacher'],rotation=0,fontsize=TYPE['tick'])
        ax.set_xlim(-.5,3.6);ax.set_ylim(38,105);ax.set_yticks([40,60,80,100])
    else:
        ax.set_xticks(list(x),DATA['budgets']);ax.set_xlabel('Soft memory budget, K',labelpad=12)
        ax.set_xlim(-.3,3.3);ax.set_ylim(72,97);ax.set_yticks([75,80,85,90,95])
    ax.legend(handles=handles,ncol=2,frameon=False,loc='upper center',bbox_to_anchor=(.5,1.17),fontsize=TYPE['legend'],handlelength=1.6,columnspacing=2,title='PERSONAMEM',title_fontsize=TYPE['eyebrow'])
    fig.subplots_adjust(left=.15,right=.97,bottom=.18,top=.81)
    save(fig,'memory-reliance.svg' if reliance else 'memory-budget.svg',tight=False)


def memory_cost(mobile=False):
    fig,ax=plt.subplots(figsize=(5.1,4.15));style(ax)
    handles=[]
    for i,(name,data) in enumerate(DATA['memory'].items()):
        color=[ACCENT,SECOND][i];marker=['o','s'][i]
        tokens=data['tokens']; y=[(value/tokens[2]-1)*100 for value in tokens]
        ax.plot(range(4),y,color=color,marker=marker,lw=2,ms=6)
        for x,(change,absolute) in enumerate(zip(y,tokens)):
            ax.annotate(f'{absolute/1000:.1f}K',(x,change),xytext=(0,11 if i==0 else -20),
                textcoords='offset points',ha='center',fontsize=TYPE['annotation'],color=color)
        handles.append(Line2D([],[],color=color,marker=marker,lw=2,label=name.replace('PersonaMem-','')))
    ax.axhline(0,color=MUTED,ls=':',lw=.8)
    ax.set_xticks(range(4),DATA['budgets'])
    ax.set(xlim=(-.3,3.3),ylim=(-2.5,7.5),yticks=[0,2,4,6],xlabel='Soft memory budget, K',ylabel='Token cost vs. K = 256 (%)')
    ax.xaxis.labelpad=12;ax.yaxis.labelpad=10
    ax.legend(handles=handles,ncol=2,frameon=False,loc='upper center',bbox_to_anchor=(.5,1.17),fontsize=TYPE['legend'],title='PERSONAMEM',title_fontsize=TYPE['eyebrow'])
    fig.subplots_adjust(left=.15,right=.97,bottom=.18,top=.81)
    save(fig,'memory-cost-mobile.svg' if mobile else 'memory-cost.svg',tight=False)

training();training(mobile=True);memory();memory(reliance=True);memory_cost();memory_cost(mobile=True)
print('Rendered 6 responsive SVG charts from manuscript data.')
