import React, {useEffect, useState} from 'react';
import {createRoot} from 'react-dom/client';

const stages = [
  ['01-baseline','Baseline','Existing tests before investigation'],
  ['02-original','Original test','First attempt on the disclosed defect'],
  ['03-original-repeat','Repeat failure','Second attempt with the same test'],
  ['04-candidate-reproducer','Candidate test','Accepted test against the existing fix'],
  ['05-candidate-regression','Regression','All baseline test identities']
];
const tabNames = ['Finding','Patch','Execution','Review'];
const pretty = value => (value || 'not recorded').replaceAll('_',' ');
const when = epoch => epoch ? new Date(epoch * 1000).toLocaleString() : 'Not recorded';
async function api(path, options) {
  const response = await fetch(path, options);
  const data = await response.json();
  if (!response.ok) throw new Error(data.error || 'The local workspace did not respond.');
  return data;
}
function Badge({value}) {
  const good = ['verified_candidate','passed','approved'].includes(value);
  return <span className={'badge '+(good?'good':value==='running'?'running':'neutral')}>{pretty(value)}</span>;
}
function App() {
  const [config,setConfig]=useState(null), [state,setState]=useState(null), [history,setHistory]=useState([]);
  const [record,setRecord]=useState(null), [selected,setSelected]=useState(null), [confirmed,setConfirmed]=useState(false);
  const [tab,setTab]=useState('Finding'), [error,setError]=useState(''), [pending,setPending]=useState(false);
  const [decision,setDecision]=useState(''), [note,setNote]=useState('');
  const [connectionError,setConnectionError]=useState('');
  useEffect(()=>{
    let disposed=false, timer;
    async function poll() {
      try {
        const next=await api('/api/state');
        if(!disposed){setState(next);setConnectionError('');timer=setTimeout(poll,next.active?1000:4000);}
      } catch(e) {if(!disposed){setConnectionError('Connection lost. Keep the local Vesper process running. '+e.message);timer=setTimeout(poll,4000);}}
    }
    api('/api/config').then(data=>{if(!disposed)setConfig(data)}).catch(e=>setError(e.message));
    poll();
    return ()=>{disposed=true;clearTimeout(timer)};
  },[]);
  useEffect(()=>{
    let disposed=false;
    api('/api/history').then(data=>{if(!disposed)setHistory(data)}).catch(e=>setError(e.message));
    if(!state?.active && state?.run_id && !selected) {
      api('/api/run/'+state.run_id).then(data=>{if(!disposed)setRecord(data)}).catch(e=>setError(e.message));
    }
    return ()=>{disposed=true};
  },[state?.active,state?.run_id,selected]);
  async function start(event) {
    event.preventDefault(); setPending(true);setError('');
    try {
      const next=await api('/api/run',{method:'POST',headers:{'Content-Type':'application/json','X-Vesper-Token':config.token},
        body:JSON.stringify({project:config.project.id,requirement_confirmed:confirmed})});
      setState(next);setRecord(null);setSelected(null);setTab('Execution');setDecision('');setNote('');
    } catch(e) {setError(e.message)} finally {setPending(false)}
  }
  async function openRun(id) {
    try {const data=await api('/api/run/'+id);setSelected(id);setRecord(data);setTab('Finding');setDecision('');setNote('');}
    catch(e){setError(e.message)}
  }
  async function saveReview(event) {
    event.preventDefault();setPending(true);setError('');
    try {
      const review=await api('/api/review/'+record.run_id,{method:'POST',headers:{'Content-Type':'application/json','X-Vesper-Token':config.token},body:JSON.stringify({decision,note})});
      setRecord({...record,review});
    } catch(e){setError(e.message)} finally {setPending(false)}
  }
  const running=Boolean(state?.active), current=running&&!selected;
  const result=current?null:record?.result;
  const attempts=current?state.stages:record?.stages || {};
  const completed=Object.values(attempts).filter(item=>item.status!=='running').length;
  const canStart=config&&confirmed&&!running&&!pending&&config.tools.java&&config.tools.maven;
  const runId=current?state.run_id:record?.run_id;
  const evidence=runId?'/evidence/'+runId+'/':null;
  const status=current?'running':result?.status || state?.phase || 'idle';
  const meaningfulFailure=result?.investigation==='reproduced';
  const reviewed=Boolean(record?.review);
  function tabsKey(event,index) {
    if(!['ArrowLeft','ArrowRight','Home','End'].includes(event.key))return;
    event.preventDefault();
    const next=event.key==='Home'?0:event.key==='End'?3:(index+(event.key==='ArrowRight'?1:3))%4;
    setTab(tabNames[next]);document.getElementById('tab-'+next).focus();
  }
  return <><a className="skip" href="#main">Skip to workspace</a>
    <aside className="rail">
      <a className="brand" href="#main"><img src="/vesper-mark.svg" alt="Ladybug with four stars"/><span>vesper</span></a>
      <p className="tagline">Clarity before acceptance.</p>
      <div className="rail-section">Workspace</div>
      <button className={!selected?'rail-link active':'rail-link'} onClick={()=>{setSelected(null);setRecord(null);setTab(running?'Execution':'Finding')}}>01 <span>Verification</span>{running?<i>Running</i>:null}</button>
      <div className="rail-section history-label">Saved runs <span>{history.length}</span></div>
      <div className="history">{history.length?history.map(item=><button className={'history-item '+(selected===item.run_id?'selected':'')} key={item.run_id} onClick={()=>openRun(item.run_id)}><span>{item.historical?'Saved R3 example':'Checkout / R3'}</span><small>{when(item.started_at)}</small><b>{item.status==='verified_candidate'?'Verified candidate':'Blocked'}</b></button>):<p className="rail-empty">Your first run will appear here.</p>}</div>
      <div className="rail-footer"><details><summary>The four stars</summary><p>Requirement<br/>Reproduction<br/>Verification<br/>Human review</p></details><span>Black Sheep Team</span><small>Local workspace · no cloud upload</small></div>
    </aside>
    <div className="shell"><header className="bar"><a className="mobile-brand" href="#main"><img src="/vesper-mark.svg" alt="Vesper four-star ladybug"/>vesper</a><span className="crumb">Workspace <b>/</b> Checkout</span><span className="connection">{connectionError?'Local verifier disconnected':state?'Local verifier connected':'Connecting to verifier…'}</span></header>
      <main id="main"><div className="intro"><div><div className="eyebrow">Verification workspace</div><h1>One requirement.<br/>A traceable decision.</h1><p>Run the checks, follow the evidence, and decide whether the candidate is ready.</p></div><div className="scope-label"><span className="scope-number">R3</span><div>Java / Maven<small>Supported checkout demo</small></div></div></div>
      {error||connectionError?<div className="error" role="alert"><strong>Workspace needs attention</strong><p>{error||connectionError}</p></div>:null}
      <form className="setup" onSubmit={start}><div className="setup-title"><div className="eyebrow">01 / Set the scope</div><span className="small-label">Disclosed seeded replay</span></div><div className="setup-grid"><div><label htmlFor="project">Project</label><select id="project" value="checkout-r3" onChange={()=>{}} disabled={running}><option value="checkout-r3">Checkout / discount service</option></select><p className="hint">Local <code>demo/</code> · one module · existing candidate fix</p><div className="tools"><span className={config?.tools.java?'available':''}>Java {config?.tools.java?'ready':'not found'}</span><span className={config?.tools.maven?'available':''}>Maven {config?.tools.maven?'ready':'not found'}</span></div></div><div className="requirement"><label htmlFor="confirm">Requirement R3</label><h2>Expiry is inclusive.</h2><p>1,000 cents · 10% discount · checkout on the expiry date → <strong>900 cents</strong>.</p><label className="confirm"><input id="confirm" type="checkbox" checked={confirmed} onChange={event=>setConfirmed(event.target.checked)} disabled={running}/>I confirm this expected behaviour for this run.</label></div></div><div className="setup-bottom"><p>The runner tests the disclosed original and an existing fix. It does not discover or author a new repair.</p><button className="primary" disabled={!canStart} type="submit">{running?'Verification running…':pending?'Starting…':'Run verification'}<span aria-hidden="true">↗</span></button></div></form>
      {config&&(!config.tools.java||!config.tools.maven)?<div className="notice">Start this workspace from a terminal with Java 17+ and Maven available. On this machine, use <code>scripts/use-local-tools.ps1</code> first.</div>:null}
      <div className="journey" aria-label="Verification journey">{[['Requirement',confirmed||Boolean(result),'Scope confirmed'],['Reproduction',meaningfulFailure,'Repeat the original test'],['Verification',result?.status==='verified_candidate','Candidate and regression'],['Human review',reviewed,'Your decision']].map(([name,done,caption],index)=><div key={name} className={done?'done':''}><span className="step-index">{done?'✓':String(index+1).padStart(2,'0')}</span><div><b>{name}</b><small>{caption}</small></div></div>)}</div>
      {(record||current||state?.error)?<section className="run-area"><div className="run-heading"><div><div className="eyebrow">02 / Evidence</div><h2>{current?'Verification in progress':record?.historical?'Saved execution record':'Verification result'}</h2><p>{record?.historical?'Historical Java execution; opened without rerunning tests.':current?'Stage updates and logs come from the running local verifier.':runId||'Execution could not start'}</p></div><Badge value={status}/></div>
        {current?<div className="run-progress"><span>{completed} of 5 attempts recorded</span><span>Actual command output</span></div>:null}
        <div className="tabs" role="tablist" aria-label="Run evidence">{tabNames.map((name,index)=><button key={name} id={'tab-'+index} role="tab" aria-selected={tab===name} aria-controls="evidence-panel" tabIndex={tab===name?0:-1} onClick={()=>setTab(name)} onKeyDown={event=>tabsKey(event,index)}>{name}</button>)}</div>
        <div className="panel" role="tabpanel" id="evidence-panel" aria-labelledby={'tab-'+tabNames.indexOf(tab)}>
          {tab==='Finding'?<><div className="finding-layout"><div><div className="eyebrow">Requirement-linked finding</div><h3>{meaningfulFailure?'Discount lost on the expiry date':'R3 expiry behaviour'}</h3><p>{result?.explanation||'The verifier has not established a conclusion yet. Follow the execution trail while the checks run.'}</p><div className="fact-row"><div><small>Expected</small><strong>900¢</strong></div><div><small>Observed on original</small><strong>{meaningfulFailure?'1,000¢':'Not confirmed'}</strong></div><div><small>Investigation</small><strong className="word-value">{pretty(result?.investigation||'pending')}</strong></div></div></div><aside className="decision-callout"><span className="eyebrow">Human decision</span><h3>{record?.review?pretty(record.review.decision):'Pending review'}</h3><p>Verification is evidence for your decision. No patch has been integrated by this workspace.</p><button className="text-button" onClick={()=>setTab('Review')}>Review this candidate →</button></aside></div><p className="limits">One disclosed seed with an existing corrected candidate. This run does not measure agent accuracy or developer time saved.</p></>:null}
          {tab==='Patch'?<><div className="panel-heading"><div><h3>Candidate changes</h3><p><code>src/main/java/dev/vesper/Checkout.java</code></p></div>{result&&evidence?<a className="secondary" href={evidence+'report.html#patch'} target="_blank" rel="noreferrer">Side-by-side report ↗</a>:null}</div>{result?.diff?<pre className="diff" aria-label="Candidate patch">{result.diff.split('\n').map((line,i)=><span className={line.startsWith('+')?'added':line.startsWith('-')?'removed':''} key={i}>{line||' '}<br/></span>)}</pre>:<p className="empty">The patch will be available with the completed evidence record.</p>}<p className="limits">The existing candidate is compared with a preserved original. This view does not apply the patch.</p></>:null}
          {tab==='Execution'?<><div className="attempts">{stages.map(([id,title,caption],index)=>{const item=attempts[id], counts=item?.counts;return <article className="attempt" key={id}><span className="attempt-number">{String(index+1).padStart(2,'0')}</span><div><div className="attempt-heading"><h3>{title}</h3><Badge value={meaningfulFailure&&['02-original','03-original-repeat'].includes(id)?'expected_failure':item?.status||'not_run'}/></div><p>{caption}</p>{counts?<div className="counts"><span>{counts.tests} tests</span><span>{counts.failures} failures</span><span>{counts.errors} errors</span><span>{counts.skipped} skipped</span><span>{item.duration_seconds}s</span></div>:null}{item&&item.status!=='running'&&evidence?<details><summary>Command and raw evidence</summary><pre>{item.command?.join(' ')||'Command not recorded'}</pre><a href={evidence+id+'/result.json'} target="_blank" rel="noreferrer">Execution record ↗</a><a href={evidence+id+'/execution.log'} target="_blank" rel="noreferrer">Full log ↗</a></details>:null}</div></article>})}</div>{current?<div className="console"><div><span>Current execution log</span><span>{pretty(state.phase)}</span></div><pre>{state.log_tail||'Preparing the next command. No output recorded yet.'}</pre></div>:null}{state?.error&&!selected?<div role="alert" className="notice">{state.error}</div>:null}<p className="limits">An original test failure is expected in this seeded replay. The final gate decision also checks the failure type, frozen inputs and regression identities.</p></>:null}
          {tab==='Review'?<><div className="panel-heading"><div><h3>A decision belongs to you.</h3><p>Inspect the finding, unchanged test and full regression evidence before recording a decision.</p></div></div>{!record?<p className="empty">Wait for verification to finish. No decision has been recorded.</p>:record.historical?<div className="notice">This historical example is read-only. Run a fresh verification to record a decision.</div>:record.review?<div className="review-saved" role="status"><Badge value={record.review.decision}/><p>Recorded {record.review.recorded_at}. No integration performed.</p><p>{record.review.note||'No additional note.'}</p><p className="hash">Patch SHA-256: {record.review.patch_sha256}</p><a href={evidence+'review.json'} target="_blank" rel="noreferrer">Open decision record ↗</a></div>:<form onSubmit={saveReview} className="review-form"><label htmlFor="decision">Your decision</label><select id="decision" value={decision} onChange={event=>setDecision(event.target.value)} required><option value="">Choose a decision…</option><option value="approved" disabled={result?.status!=='verified_candidate'}>Approve candidate for later integration</option><option value="changes_requested">Request changes</option></select><label htmlFor="note">Review note <span>(optional)</span></label><textarea id="note" rows="3" maxLength="2000" value={note} onChange={event=>setNote(event.target.value)}/><p className="hint">Saves a separate decision tied to this patch fingerprint. It does not edit the source, merge, or publish.</p><button type="submit" className="primary" disabled={!decision||pending}>Record my decision</button></form>}<p className="limits">Saved execution evidence stays unchanged. A decision is stored separately and cannot be silently overwritten.</p></>:null}
        </div>{record?<div className="exports"><span>Keep the evidence with the patch.</span><a href={evidence+'report.html'} target="_blank" rel="noreferrer">Open full report ↗</a><a href={evidence+'workflow.json'} target="_blank" rel="noreferrer">Run JSON ↗</a><a href={evidence+'report.md'} target="_blank" rel="noreferrer">Markdown ↗</a></div>:null}
      </section>:<section className="welcome"><div className="eyebrow">Ready when you are</div><h2>Confirm the rule. Then let the checks run.</h2><p>Vesper will establish the baseline, reproduce the original failure twice, check the candidate and verify regression scope.</p>{history[0]?<button className="text-button" onClick={()=>openRun(history[0].run_id)}>Or inspect a saved run →</button>:null}</section>}
      <footer><span>vesper · evidence before acceptance</span><a href="/licenses.txt" target="_blank" rel="noreferrer">Open-source notices</a><span>Local execution · no automated merge</span></footer>
      </main></div></>;
}
createRoot(document.getElementById('root')).render(<App/>);
