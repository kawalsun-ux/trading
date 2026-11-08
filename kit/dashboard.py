"""Generate a self-contained HTML dashboard (stdlib only)."""
import json

def render(title, prices, entries=None, exits=None):
    entries = entries or []
    exits = exits or []
    html = f"""<!DOCTYPE html>
<html><head><meta charset="utf-8"><title>{title}</title>
<style>body{{font-family:sans-serif;margin:20px}}canvas{{border:1px solid #ccc}}</style>
</head><body>
<h2>{title}</h2>
<canvas id="c" width="900" height="400"></canvas>
<script>
const prices={json.dumps(prices)};
const entries={json.dumps(entries)};
const exits={json.dumps(exits)};
const c=document.getElementById('c'),ctx=c.getContext('2d');
const pad=40, w=c.width-pad*2, h=c.height-pad*2;
const mn=Math.min(...prices), mx=Math.max(...prices);
const sx=i=>pad+i*(w/(prices.length-1));
const sy=v=>pad+h-(v-mn)/(mx-mn)*h;
ctx.beginPath();
prices.forEach((v,i)=>{{ if(i===0)ctx.moveTo(sx(i),sy(v)); else ctx.lineTo(sx(i),sy(v)); }});
ctx.strokeStyle='#2563eb';ctx.lineWidth=2;ctx.stroke();
entries.forEach(i=>{{ctx.fillStyle='green';ctx.beginPath();ctx.arc(sx(i),sy(prices[i]),5,0,Math.PI*2);ctx.fill();}});
exits.forEach(i=>{{ctx.fillStyle='red';ctx.beginPath();ctx.arc(sx(i),sy(prices[i]),5,0,Math.PI*2);ctx.fill();}});
</script></body></html>"""
    return html