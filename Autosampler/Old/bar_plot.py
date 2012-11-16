<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">
  
  


  <head>
    <title>
      bar_plot.py in Chaco/trunk/examples
     – ETS
    </title>
    <meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />
        <link rel="search" href="/enthought/search" />
        <link rel="help" href="/enthought/wiki/TracGuide" />
        <link rel="alternate" href="/enthought/browser/Chaco/trunk/examples/bar_plot.py?format=txt" type="text/plain" title="Plain Text" /><link rel="alternate" href="/enthought/export/26451/Chaco/trunk/examples/bar_plot.py" type="text/x-python; charset=iso-8859-15" title="Original Format" />
        <link rel="tracwysiwyg.base" href="/enthought" />
        <link rel="start" href="/enthought/wiki" />
        <link rel="stylesheet" href="/trac/css/trac.css" type="text/css" /><link rel="stylesheet" href="/trac/css/code.css" type="text/css" /><link rel="stylesheet" href="/enthought/pygments/trac.css" type="text/css" /><link rel="stylesheet" href="/trac/css/browser.css" type="text/css" /><link rel="stylesheet" href="/enthought/chrome/tracwysiwyg/wysiwyg.css" type="text/css" /><link rel="stylesheet" href="/enthought/chrome/mindmap/ui.theme.css" type="text/css" /><link rel="stylesheet" href="/enthought/chrome/mindmap/ui.resizable.css" type="text/css" /><link rel="stylesheet" href="/enthought/chrome/listofwikipages/style.css" type="text/css" /><link rel="stylesheet" href="/enthought/themeengine/theme.css" type="text/css" />
        <link rel="tracwysiwyg.stylesheet" href="/trac/css/trac.css" /><link rel="tracwysiwyg.stylesheet" href="/enthought/chrome/tracwysiwyg/editor.css" />
        <link rel="prev" href="/enthought/browser/Chaco/trunk/examples/bar_plot.py?rev=22872" title="Revision 22872" />
        <link rel="shortcut icon" href="/enthought/chrome/common/trac.ico" type="image/x-icon" />
        <link rel="icon" href="/enthought/chrome/common/trac.ico" type="image/x-icon" />
      <link type="application/opensearchdescription+xml" rel="search" href="/enthought/search/opensearch" title="Search ETS" />
    <script type="text/javascript">
      var _tracwysiwyg={"escapeNewlines":false};
    </script>
    <script type="text/javascript" src="/trac/js/jquery.js"></script><script type="text/javascript" src="/trac/js/babel.js"></script><script type="text/javascript" src="/trac/js/trac.js"></script><script type="text/javascript" src="/trac/js/search.js"></script><script type="text/javascript" src="/enthought/chrome/tracwysiwyg/wysiwyg.js"></script><script type="text/javascript" src="/enthought/chrome/tracwysiwyg/wysiwyg-load.js"></script><script type="text/javascript" src="/enthought/chrome/mindmap/tools.flashembed-1.0.4.min.js"></script><script type="text/javascript" src="/enthought/chrome/mindmap/mindmap.js"></script><script type="text/javascript" src="/enthought/chrome/mindmap/ui.core.js"></script><script type="text/javascript" src="/enthought/chrome/mindmap/ui.resizable.js"></script>
    <!--[if lt IE 7]>
    <script type="text/javascript" src="/trac/js/ie_pre7_hacks.js"></script>
    <![endif]-->
    <script type="text/javascript" src="/trac/js/folding.js"></script><script type="text/javascript">
      jQuery(document).ready(function($) {
        $(".trac-toggledeleted").show().click(function() {
                  $(this).siblings().find(".trac-deleted").toggle();
                  return false;
        }).click();
        $("#jumploc input").hide();
        $("#jumploc select").change(function () {
          this.parentNode.parentNode.submit();
        });
          $('#preview table.code').enableCollapsibleColumns($('#preview table.code thead th.content'));
      });
    </script>
  </head>
  <body>
    <div id="banner">
      <div id="header">
        <a id="logo" href="https://svn.enthought.com/enthought/"><img src="/images/etlogo.gif" alt="Enthought Tools Suite" height="50" width="212" /></a>
      </div>
      <form id="search" action="/enthought/search" method="get">
        <div>
          <label for="proj-search">Search:</label>
          <input type="text" id="proj-search" name="q" size="18" value="" />
          <input type="submit" value="Search" />
        </div>
      </form>
      <div id="metanav" class="nav">
    <ul>
      <li class="first"><a href="/enthought/login">Login</a></li><li><a href="/enthought/prefs">Preferences</a></li><li><a href="/enthought/wiki/TracGuide">Help/Guide</a></li><li><a href="/enthought/about">About Trac</a></li><li class="last"><a href="/enthought/register">Register</a></li>
    </ul>
  </div>
    </div>
    <div id="mainnav" class="nav">
    <ul>
      <li class="first"><a href="/enthought/wiki">Wiki</a></li><li><a href="/enthought/timeline">Timeline</a></li><li><a href="/enthought/roadmap">Roadmap</a></li><li class="active"><a href="/enthought/browser">Browse Source</a></li><li><a href="/enthought/query">View Tickets</a></li><li class="last"><a href="/enthought/search">Search</a></li>
    </ul>
  </div>
    <div id="main">
      <div id="ctxtnav" class="nav">
        <h2>Context Navigation</h2>
          <ul>
              <li class="first"><span>&larr; <a class="prev" href="/enthought/browser/Chaco/trunk/examples/bar_plot.py?rev=22872" title="Revision 22872">Previous Revision</a></span></li><li><span class="missing">Next Revision &rarr;</span></li><li><a href="/enthought/browser/Chaco/trunk/examples/bar_plot.py?annotate=blame&amp;rev=25284" title="Annotate each line with the last changed revision (this can be time consuming...)">Annotate</a></li><li class="last"><a href="/enthought/log/Chaco/trunk/examples/bar_plot.py">Revision Log</a></li>
          </ul>
        <hr />
      </div>
    <div id="content" class="browser">
          <h1>
<a class="pathentry first" href="/enthought/browser?order=name" title="Go to repository root">source:</a>
<a class="pathentry" href="/enthought/browser/Chaco?order=name" title="View Chaco">Chaco</a><span class="pathentry sep">/</span><a class="pathentry" href="/enthought/browser/Chaco/trunk?order=name" title="View trunk">trunk</a><span class="pathentry sep">/</span><a class="pathentry" href="/enthought/browser/Chaco/trunk/examples?order=name" title="View examples">examples</a><span class="pathentry sep">/</span><a class="pathentry" href="/enthought/browser/Chaco/trunk/examples/bar_plot.py?order=name" title="View bar_plot.py">bar_plot.py</a>
<span class="pathentry sep">@</span>
  <a class="pathentry" href="/enthought/changeset/25284" title="View changeset 25284">25284</a>
<br style="clear: both" />
</h1>
        <div id="jumprev">
          <form action="" method="get">
            <div>
              <label for="rev">
                View revision:</label>
              <input type="text" id="rev" name="rev" size="6" />
            </div>
          </form>
        </div>
      <table id="info" summary="Revision info">
        <tr>
          <th scope="col">Revision <a href="/enthought/changeset/25284">25284</a>,
            <span title="4663 bytes">4.6 KB</span>
            checked in by bhendrix, <a class="timeline" href="/enthought/timeline?from=2010-02-22T16%3A22%3A23-06%3A00&amp;precision=second" title="2010-02-22T16:22:23-06:00 in Timeline">20 months</a> ago
            (<a href="/enthought/changeset/25284/Chaco/trunk/examples/bar_plot.py">diff</a>)</th>
        </tr>
        <tr>
          <td class="message searchable">
              <p>
fixed a inconsistent indent and removed unused imports<br />
</p>
          </td>
        </tr>
        <tr>
          <td colspan="2">
            <ul class="props">
              <li>
                  Property <strong>svn:eol-style</strong> set to
                  <em><code>native</code></em>
              </li><li>
                  Property <strong>svn:keywords</strong> set to
                  <em><code>Id</code></em>
              </li>
            </ul>
          </td>
        </tr>
      </table>
      <div id="preview" class="searchable">
        
  <table class="code"><thead><tr><th class="lineno" title="Line numbers">Line</th><th class="content"> </th></tr></thead><tbody><tr><th id="L1"><a href="#L1">1</a></th><td></td></tr><tr><th id="L2"><a href="#L2">2</a></th><td><span class="c"># Major library imports</span></td></tr><tr><th id="L3"><a href="#L3">3</a></th><td><span class="kn">from</span> <span class="nn">numpy</span> <span class="kn">import</span> cos<span class="p">,</span> linspace<span class="p">,</span> pi<span class="p">,</span> sin</td></tr><tr><th id="L4"><a href="#L4">4</a></th><td></td></tr><tr><th id="L5"><a href="#L5">5</a></th><td><span class="kn">from</span> <span class="nn">enthought.chaco.example_support</span> <span class="kn">import</span> COLOR_PALETTE</td></tr><tr><th id="L6"><a href="#L6">6</a></th><td><span class="kn">from</span> <span class="nn">enthought.enable.example_support</span> <span class="kn">import</span> DemoFrame<span class="p">,</span> demo_main</td></tr><tr><th id="L7"><a href="#L7">7</a></th><td></td></tr><tr><th id="L8"><a href="#L8">8</a></th><td><span class="c"># Enthought library imports</span></td></tr><tr><th id="L9"><a href="#L9">9</a></th><td><span class="kn">from</span> <span class="nn">enthought.enable.api</span> <span class="kn">import</span> Component<span class="p">,</span> ComponentEditor<span class="p">,</span> Window</td></tr><tr><th id="L10"><a href="#L10">10</a></th><td><span class="kn">from</span> <span class="nn">enthought.traits.api</span> <span class="kn">import</span> HasTraits<span class="p">,</span> Instance</td></tr><tr><th id="L11"><a href="#L11">11</a></th><td><span class="kn">from</span> <span class="nn">enthought.traits.ui.api</span> <span class="kn">import</span> Item<span class="p">,</span> Group<span class="p">,</span> View</td></tr><tr><th id="L12"><a href="#L12">12</a></th><td></td></tr><tr><th id="L13"><a href="#L13">13</a></th><td><span class="c"># Chaco imports</span></td></tr><tr><th id="L14"><a href="#L14">14</a></th><td><span class="kn">from</span> <span class="nn">enthought.chaco.api</span> <span class="kn">import</span> ArrayDataSource<span class="p">,</span> BarPlot<span class="p">,</span> DataRange1D<span class="p">,</span> LabelAxis<span class="p">,</span> \</td></tr><tr><th id="L15"><a href="#L15">15</a></th><td>                                 LinearMapper<span class="p">,</span> OverlayPlotContainer<span class="p">,</span> PlotAxis</td></tr><tr><th id="L16"><a href="#L16">16</a></th><td></td></tr><tr><th id="L17"><a href="#L17">17</a></th><td></td></tr><tr><th id="L18"><a href="#L18">18</a></th><td><span class="k">def</span> <span class="nf">get_points</span><span class="p">():</span></td></tr><tr><th id="L19"><a href="#L19">19</a></th><td>    index <span class="o">=</span> linspace<span class="p">(</span>pi<span class="o">/</span><span class="mi">4</span><span class="p">,</span> <span class="mi">3</span><span class="o">*</span>pi<span class="o">/</span><span class="mi">2</span><span class="p">,</span> <span class="mi">9</span><span class="p">)</span></td></tr><tr><th id="L20"><a href="#L20">20</a></th><td>    data <span class="o">=</span> sin<span class="p">(</span>index<span class="p">)</span> <span class="o">+</span> <span class="mi">2</span></td></tr><tr><th id="L21"><a href="#L21">21</a></th><td>    <span class="k">return</span> <span class="p">(</span><span class="nb">range</span><span class="p">(</span><span class="mi">1</span><span class="p">,</span> <span class="mi">10</span><span class="p">),</span> data<span class="p">)</span></td></tr><tr><th id="L22"><a href="#L22">22</a></th><td>    </td></tr><tr><th id="L23"><a href="#L23">23</a></th><td><span class="k">def</span> <span class="nf">make_curves</span><span class="p">():</span></td></tr><tr><th id="L24"><a href="#L24">24</a></th><td>    <span class="p">(</span>index_points<span class="p">,</span> value_points<span class="p">)</span> <span class="o">=</span> get_points<span class="p">()</span></td></tr><tr><th id="L25"><a href="#L25">25</a></th><td>    size <span class="o">=</span> <span class="nb">len</span><span class="p">(</span>index_points<span class="p">)</span></td></tr><tr><th id="L26"><a href="#L26">26</a></th><td></td></tr><tr><th id="L27"><a href="#L27">27</a></th><td>    <span class="c"># Create our data sources</span></td></tr><tr><th id="L28"><a href="#L28">28</a></th><td>    idx <span class="o">=</span> ArrayDataSource<span class="p">(</span>index_points<span class="p">[:(</span>size<span class="o">/</span><span class="mi">2</span><span class="p">)])</span></td></tr><tr><th id="L29"><a href="#L29">29</a></th><td>    vals <span class="o">=</span> ArrayDataSource<span class="p">(</span>value_points<span class="p">[:(</span>size<span class="o">/</span><span class="mi">2</span><span class="p">)],</span> sort_order<span class="o">=</span><span class="s">"none"</span><span class="p">)</span></td></tr><tr><th id="L30"><a href="#L30">30</a></th><td></td></tr><tr><th id="L31"><a href="#L31">31</a></th><td>    idx2 <span class="o">=</span> ArrayDataSource<span class="p">(</span>index_points<span class="p">[(</span>size<span class="o">/</span><span class="mi">2</span><span class="p">):])</span></td></tr><tr><th id="L32"><a href="#L32">32</a></th><td>    vals2 <span class="o">=</span> ArrayDataSource<span class="p">(</span>value_points<span class="p">[(</span>size<span class="o">/</span><span class="mi">2</span><span class="p">):],</span> sort_order<span class="o">=</span><span class="s">"none"</span><span class="p">)</span></td></tr><tr><th id="L33"><a href="#L33">33</a></th><td></td></tr><tr><th id="L34"><a href="#L34">34</a></th><td>    idx3 <span class="o">=</span> ArrayDataSource<span class="p">(</span>index_points<span class="p">)</span></td></tr><tr><th id="L35"><a href="#L35">35</a></th><td>    starting_vals <span class="o">=</span> ArrayDataSource<span class="p">(</span>value_points<span class="p">,</span> sort_order<span class="o">=</span><span class="s">"none"</span><span class="p">)</span></td></tr><tr><th id="L36"><a href="#L36">36</a></th><td>    vals3 <span class="o">=</span> ArrayDataSource<span class="p">(</span><span class="mi">2</span> <span class="o">*</span> cos<span class="p">(</span>value_points<span class="p">)</span> <span class="o">+</span> <span class="mi">2</span><span class="p">,</span> sort_order<span class="o">=</span><span class="s">"none"</span><span class="p">)</span></td></tr><tr><th id="L37"><a href="#L37">37</a></th><td></td></tr><tr><th id="L38"><a href="#L38">38</a></th><td>    <span class="c"># Create the index range</span></td></tr><tr><th id="L39"><a href="#L39">39</a></th><td>    index_range <span class="o">=</span> DataRange1D<span class="p">(</span>idx<span class="p">,</span> low<span class="o">=</span><span class="mf">0.5</span><span class="p">,</span> high<span class="o">=</span><span class="mf">9.5</span><span class="p">)</span></td></tr><tr><th id="L40"><a href="#L40">40</a></th><td>    index_mapper <span class="o">=</span> LinearMapper<span class="p">(</span><span class="nb">range</span><span class="o">=</span>index_range<span class="p">)</span></td></tr><tr><th id="L41"><a href="#L41">41</a></th><td></td></tr><tr><th id="L42"><a href="#L42">42</a></th><td>    <span class="c"># Create the value range</span></td></tr><tr><th id="L43"><a href="#L43">43</a></th><td>    value_range <span class="o">=</span> DataRange1D<span class="p">(</span>low<span class="o">=</span><span class="mi">0</span><span class="p">,</span> high<span class="o">=</span><span class="mf">4.25</span><span class="p">)</span></td></tr><tr><th id="L44"><a href="#L44">44</a></th><td>    value_mapper <span class="o">=</span> LinearMapper<span class="p">(</span><span class="nb">range</span><span class="o">=</span>value_range<span class="p">)</span></td></tr><tr><th id="L45"><a href="#L45">45</a></th><td></td></tr><tr><th id="L46"><a href="#L46">46</a></th><td>    <span class="c"># Create the plot</span></td></tr><tr><th id="L47"><a href="#L47">47</a></th><td>    plot1 <span class="o">=</span> BarPlot<span class="p">(</span>index<span class="o">=</span>idx<span class="p">,</span> value<span class="o">=</span>vals<span class="p">,</span></td></tr><tr><th id="L48"><a href="#L48">48</a></th><td>                    value_mapper<span class="o">=</span>value_mapper<span class="p">,</span></td></tr><tr><th id="L49"><a href="#L49">49</a></th><td>                    index_mapper<span class="o">=</span>index_mapper<span class="p">,</span></td></tr><tr><th id="L50"><a href="#L50">50</a></th><td>                    line_color<span class="o">=</span><span class="s">'black'</span><span class="p">,</span></td></tr><tr><th id="L51"><a href="#L51">51</a></th><td>                    fill_color<span class="o">=</span><span class="nb">tuple</span><span class="p">(</span>COLOR_PALETTE<span class="p">[</span><span class="mi">6</span><span class="p">]),</span></td></tr><tr><th id="L52"><a href="#L52">52</a></th><td>                    bar_width<span class="o">=</span><span class="mf">0.8</span><span class="p">,</span> antialias<span class="o">=</span><span class="bp">False</span><span class="p">)</span></td></tr><tr><th id="L53"><a href="#L53">53</a></th><td>    </td></tr><tr><th id="L54"><a href="#L54">54</a></th><td>    plot2 <span class="o">=</span> BarPlot<span class="p">(</span>index<span class="o">=</span>idx2<span class="p">,</span> value<span class="o">=</span>vals2<span class="p">,</span></td></tr><tr><th id="L55"><a href="#L55">55</a></th><td>                    value_mapper<span class="o">=</span>value_mapper<span class="p">,</span></td></tr><tr><th id="L56"><a href="#L56">56</a></th><td>                    index_mapper<span class="o">=</span>index_mapper<span class="p">,</span></td></tr><tr><th id="L57"><a href="#L57">57</a></th><td>                    line_color<span class="o">=</span><span class="s">'blue'</span><span class="p">,</span></td></tr><tr><th id="L58"><a href="#L58">58</a></th><td>                    fill_color<span class="o">=</span><span class="nb">tuple</span><span class="p">(</span>COLOR_PALETTE<span class="p">[</span><span class="mi">3</span><span class="p">]),</span></td></tr><tr><th id="L59"><a href="#L59">59</a></th><td>                    bar_width<span class="o">=</span><span class="mf">0.8</span><span class="p">,</span> antialias<span class="o">=</span><span class="bp">False</span><span class="p">)</span></td></tr><tr><th id="L60"><a href="#L60">60</a></th><td>    </td></tr><tr><th id="L61"><a href="#L61">61</a></th><td>    plot3 <span class="o">=</span> BarPlot<span class="p">(</span>index<span class="o">=</span>idx3<span class="p">,</span> value<span class="o">=</span>vals3<span class="p">,</span></td></tr><tr><th id="L62"><a href="#L62">62</a></th><td>                    value_mapper<span class="o">=</span>value_mapper<span class="p">,</span></td></tr><tr><th id="L63"><a href="#L63">63</a></th><td>                    index_mapper<span class="o">=</span>index_mapper<span class="p">,</span></td></tr><tr><th id="L64"><a href="#L64">64</a></th><td>                    starting_value<span class="o">=</span>starting_vals<span class="p">,</span></td></tr><tr><th id="L65"><a href="#L65">65</a></th><td>                    line_color<span class="o">=</span><span class="s">'black'</span><span class="p">,</span></td></tr><tr><th id="L66"><a href="#L66">66</a></th><td>                    fill_color<span class="o">=</span><span class="nb">tuple</span><span class="p">(</span>COLOR_PALETTE<span class="p">[</span><span class="mi">1</span><span class="p">]),</span></td></tr><tr><th id="L67"><a href="#L67">67</a></th><td>                    bar_width<span class="o">=</span><span class="mf">0.8</span><span class="p">,</span> antialias<span class="o">=</span><span class="bp">False</span><span class="p">)</span></td></tr><tr><th id="L68"><a href="#L68">68</a></th><td></td></tr><tr><th id="L69"><a href="#L69">69</a></th><td>    <span class="k">return</span> <span class="p">[</span>plot1<span class="p">,</span> plot2<span class="p">,</span> plot3<span class="p">]</span></td></tr><tr><th id="L70"><a href="#L70">70</a></th><td></td></tr><tr><th id="L71"><a href="#L71">71</a></th><td><span class="c">#===============================================================================</span></td></tr><tr><th id="L72"><a href="#L72">72</a></th><td><span class="c"># # Create the Chaco plot.</span></td></tr><tr><th id="L73"><a href="#L73">73</a></th><td><span class="c">#===============================================================================</span></td></tr><tr><th id="L74"><a href="#L74">74</a></th><td><span class="k">def</span> <span class="nf">_create_plot_component</span><span class="p">():</span></td></tr><tr><th id="L75"><a href="#L75">75</a></th><td>    </td></tr><tr><th id="L76"><a href="#L76">76</a></th><td>    container <span class="o">=</span> OverlayPlotContainer<span class="p">(</span>bgcolor <span class="o">=</span> <span class="s">"white"</span><span class="p">)</span></td></tr><tr><th id="L77"><a href="#L77">77</a></th><td>    plots <span class="o">=</span> make_curves<span class="p">()</span></td></tr><tr><th id="L78"><a href="#L78">78</a></th><td>    <span class="k">for</span> plot <span class="ow">in</span> plots<span class="p">:</span></td></tr><tr><th id="L79"><a href="#L79">79</a></th><td>        plot<span class="o">.</span>padding <span class="o">=</span> <span class="mi">50</span></td></tr><tr><th id="L80"><a href="#L80">80</a></th><td>        container<span class="o">.</span>add<span class="p">(</span>plot<span class="p">)</span></td></tr><tr><th id="L81"><a href="#L81">81</a></th><td></td></tr><tr><th id="L82"><a href="#L82">82</a></th><td>    left_axis <span class="o">=</span> PlotAxis<span class="p">(</span>plot<span class="p">,</span> orientation<span class="o">=</span><span class="s">'left'</span><span class="p">)</span></td></tr><tr><th id="L83"><a href="#L83">83</a></th><td></td></tr><tr><th id="L84"><a href="#L84">84</a></th><td>    bottom_axis <span class="o">=</span> LabelAxis<span class="p">(</span>plot<span class="p">,</span> orientation<span class="o">=</span><span class="s">'bottom'</span><span class="p">,</span></td></tr><tr><th id="L85"><a href="#L85">85</a></th><td>                           title<span class="o">=</span><span class="s">'Categories'</span><span class="p">,</span></td></tr><tr><th id="L86"><a href="#L86">86</a></th><td>                           positions <span class="o">=</span> <span class="nb">range</span><span class="p">(</span><span class="mi">1</span><span class="p">,</span> <span class="mi">10</span><span class="p">),</span></td></tr><tr><th id="L87"><a href="#L87">87</a></th><td>                           labels <span class="o">=</span> <span class="p">[</span><span class="s">'a'</span><span class="p">,</span> <span class="s">'b'</span><span class="p">,</span> <span class="s">'c'</span><span class="p">,</span> <span class="s">'d'</span><span class="p">,</span> <span class="s">'e'</span><span class="p">,</span></td></tr><tr><th id="L88"><a href="#L88">88</a></th><td>                                     <span class="s">'f'</span><span class="p">,</span> <span class="s">'g'</span><span class="p">,</span> <span class="s">'h'</span><span class="p">,</span> <span class="s">'i'</span><span class="p">],</span></td></tr><tr><th id="L89"><a href="#L89">89</a></th><td>                           small_haxis_style<span class="o">=</span><span class="bp">True</span><span class="p">)</span></td></tr><tr><th id="L90"><a href="#L90">90</a></th><td></td></tr><tr><th id="L91"><a href="#L91">91</a></th><td>    plot<span class="o">.</span>underlays<span class="o">.</span>append<span class="p">(</span>left_axis<span class="p">)</span></td></tr><tr><th id="L92"><a href="#L92">92</a></th><td>    plot<span class="o">.</span>underlays<span class="o">.</span>append<span class="p">(</span>bottom_axis<span class="p">)</span></td></tr><tr><th id="L93"><a href="#L93">93</a></th><td>        </td></tr><tr><th id="L94"><a href="#L94">94</a></th><td>    <span class="k">return</span> container</td></tr><tr><th id="L95"><a href="#L95">95</a></th><td></td></tr><tr><th id="L96"><a href="#L96">96</a></th><td><span class="c">#===============================================================================</span></td></tr><tr><th id="L97"><a href="#L97">97</a></th><td><span class="c"># Attributes to use for the plot view.</span></td></tr><tr><th id="L98"><a href="#L98">98</a></th><td>size <span class="o">=</span> <span class="p">(</span><span class="mi">800</span><span class="p">,</span> <span class="mi">600</span><span class="p">)</span></td></tr><tr><th id="L99"><a href="#L99">99</a></th><td>title <span class="o">=</span> <span class="s">"Bar Plot"</span></td></tr><tr><th id="L100"><a href="#L100">100</a></th><td>        </td></tr><tr><th id="L101"><a href="#L101">101</a></th><td><span class="c">#===============================================================================</span></td></tr><tr><th id="L102"><a href="#L102">102</a></th><td><span class="c"># # Demo class that is used by the demo.py application.</span></td></tr><tr><th id="L103"><a href="#L103">103</a></th><td><span class="c">#===============================================================================</span></td></tr><tr><th id="L104"><a href="#L104">104</a></th><td><span class="k">class</span> <span class="nc">Demo</span><span class="p">(</span>HasTraits<span class="p">):</span></td></tr><tr><th id="L105"><a href="#L105">105</a></th><td>    plot <span class="o">=</span> Instance<span class="p">(</span>Component<span class="p">)</span></td></tr><tr><th id="L106"><a href="#L106">106</a></th><td>    </td></tr><tr><th id="L107"><a href="#L107">107</a></th><td>    traits_view <span class="o">=</span> View<span class="p">(</span></td></tr><tr><th id="L108"><a href="#L108">108</a></th><td>                    Group<span class="p">(</span></td></tr><tr><th id="L109"><a href="#L109">109</a></th><td>                        Item<span class="p">(</span><span class="s">'plot'</span><span class="p">,</span> editor<span class="o">=</span>ComponentEditor<span class="p">(</span>size<span class="o">=</span>size<span class="p">),</span> </td></tr><tr><th id="L110"><a href="#L110">110</a></th><td>                             show_label<span class="o">=</span><span class="bp">False</span><span class="p">),</span></td></tr><tr><th id="L111"><a href="#L111">111</a></th><td>                        orientation <span class="o">=</span> <span class="s">"vertical"</span><span class="p">),</span></td></tr><tr><th id="L112"><a href="#L112">112</a></th><td>                    resizable<span class="o">=</span><span class="bp">True</span><span class="p">,</span> title<span class="o">=</span>title</td></tr><tr><th id="L113"><a href="#L113">113</a></th><td>                    <span class="p">)</span></td></tr><tr><th id="L114"><a href="#L114">114</a></th><td>    </td></tr><tr><th id="L115"><a href="#L115">115</a></th><td>    <span class="k">def</span> <span class="nf">_plot_default</span><span class="p">(</span><span class="bp">self</span><span class="p">):</span></td></tr><tr><th id="L116"><a href="#L116">116</a></th><td>        <span class="k">return</span> _create_plot_component<span class="p">()</span></td></tr><tr><th id="L117"><a href="#L117">117</a></th><td>    </td></tr><tr><th id="L118"><a href="#L118">118</a></th><td>demo <span class="o">=</span> Demo<span class="p">()</span></td></tr><tr><th id="L119"><a href="#L119">119</a></th><td></td></tr><tr><th id="L120"><a href="#L120">120</a></th><td><span class="c">#===============================================================================</span></td></tr><tr><th id="L121"><a href="#L121">121</a></th><td><span class="c"># Stand-alone frame to display the plot.</span></td></tr><tr><th id="L122"><a href="#L122">122</a></th><td><span class="c">#===============================================================================</span></td></tr><tr><th id="L123"><a href="#L123">123</a></th><td><span class="k">class</span> <span class="nc">PlotFrame</span><span class="p">(</span>DemoFrame<span class="p">):</span></td></tr><tr><th id="L124"><a href="#L124">124</a></th><td></td></tr><tr><th id="L125"><a href="#L125">125</a></th><td>    <span class="k">def</span> <span class="nf">_create_window</span><span class="p">(</span><span class="bp">self</span><span class="p">):</span></td></tr><tr><th id="L126"><a href="#L126">126</a></th><td>        <span class="c"># Return a window containing our plots</span></td></tr><tr><th id="L127"><a href="#L127">127</a></th><td>        <span class="k">return</span> Window<span class="p">(</span><span class="bp">self</span><span class="p">,</span> <span class="o">-</span><span class="mi">1</span><span class="p">,</span> component<span class="o">=</span>_create_plot_component<span class="p">())</span></td></tr><tr><th id="L128"><a href="#L128">128</a></th><td>    </td></tr><tr><th id="L129"><a href="#L129">129</a></th><td><span class="k">if</span> __name__ <span class="o">==</span> <span class="s">"__main__"</span><span class="p">:</span></td></tr><tr><th id="L130"><a href="#L130">130</a></th><td>    demo_main<span class="p">(</span>PlotFrame<span class="p">,</span> size<span class="o">=</span>size<span class="p">,</span> title<span class="o">=</span>title<span class="p">)</span></td></tr><tr><th id="L131"><a href="#L131">131</a></th><td></td></tr><tr><th id="L132"><a href="#L132">132</a></th><td><span class="c">#--EOF---</span></td></tr></tbody></table>

      </div>
      <div id="help"><strong>Note:</strong> See <a href="/enthought/wiki/TracBrowser">TracBrowser</a>
        for help on using the repository browser.</div>
      <div id="anydiff">
        <form action="/enthought/diff" method="get">
          <div class="buttons">
            <input type="hidden" name="new_path" value="/Chaco/trunk/examples/bar_plot.py" />
            <input type="hidden" name="old_path" value="/Chaco/trunk/examples/bar_plot.py" />
            <input type="hidden" name="new_rev" />
            <input type="hidden" name="old_rev" />
            <input type="submit" value="View changes..." title="Select paths and revs for Diff" />
          </div>
        </form>
      </div>
    </div>
    <div id="altlinks">
      <h3>Download in other formats:</h3>
      <ul>
        <li class="first">
          <a rel="nofollow" href="/enthought/browser/Chaco/trunk/examples/bar_plot.py?format=txt">Plain Text</a>
        </li><li class="last">
          <a rel="nofollow" href="/enthought/export/26451/Chaco/trunk/examples/bar_plot.py">Original Format</a>
        </li>
      </ul>
    </div>
    </div>
    <div id="footer" lang="en" xml:lang="en"><hr />
      <a id="tracpowered" href="http://trac.edgewall.org/"><img src="/trac/trac_logo_mini.png" height="30" width="107" alt="Trac Powered" /></a>
      <p class="left">Powered by <a href="/enthought/about"><strong>Trac 0.12</strong></a><br />
        By <a href="http://www.edgewall.org/">Edgewall Software</a>.</p>
      <p class="right">Visit the Enthought home page at <a href="http://www.enthought.com/">http://www.enthought.com/</a></p>
    </div>
  </body>
</html>