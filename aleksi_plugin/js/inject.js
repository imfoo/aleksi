//var aleksi_dialog_html = '<ul id="aleksi_tabs" role="tablist" class="ui-tabs-nav ui-corner-all ui-helper-reset ui-helper-clearfix ui-widget-header ui-draggable-handle ui-dialog-titlebar ui-tabs ui-widget ui-widget-content"> <li role="tab" tabindex="0" class="ui-tabs-tab ui-corner-top ui-state-default ui-tab ui-tabs-active ui-state-active" aria-controls="aleksi_main" aria-labelledby="aleksi_word" aria-selected="true" aria-expanded="true"> <a href="#aleksi_main" id="aleksi_word" role="presentation" tabindex="-1" class="ui-tabs-anchor">valmistui</a> </li> <li role="tab" tabindex="-1" class="ui-tabs-tab ui-corner-top ui-state-default ui-tab" aria-controls="aleksi_pins" aria-labelledby="ui-id-1" aria-selected="false" aria-expanded="false"> <a href="#aleksi_pins" role="presentation" tabindex="-1" class="ui-tabs-anchor" id="ui-id-1"> Pins </a> </li> <li id="ui-tab-dialog-close"> </li> </ul> <div id="yui3-cssreset"> <div id="aleksi" class="ui-tabs ui-corner-all ui-widget ui-widget-content"> <div id="aleksi_dialog"> <div id="aleksi_main" aria-labelledby="aleksi_word" role="tabpanel" class="ui-tabs-panel ui-corner-bottom ui-widget-content" aria-hidden="false"> <span id="requesting_analysis" style="display: none;"> Requesting analysis...  </span> <span id="analysis_failed" style="display: none;"> Analysis failed, no results found.  </span> <span id="analysis_results" style="display: inline;"> <p> Dictionary entries: </p> <span> <table id="aleksi_translations_table"> </table> </span> <p> Morphological analysis: </p> <span> <span id="aleksi_morph_tag_tables"> <table class="aleksi_morph_tag_table"><tbody><tr><td class="aleksi_table_heading">Class</td><td>noun</td></tr><tr><td class="aleksi_table_heading">Case</td><td>translative</td></tr><tr><td class="aleksi_table_heading">Number</td><td>singular</td></tr><tr><td class="aleksi_table_heading">Base word</td><td>ylioppilas</td></tr><tr><td class="aleksi_table_heading">Morphemes</td><td>+yli+oppilas(oppilas)</td></tr></tbody></table></span> </span> <div class="reference"> Powered by <a class="reference" href="http://voikko.puimula.org/"> Voikko </a> </div> </span> </div> <div id="aleksi_pins" aria-labelledby="ui-id-1" role="tabpanel" class="ui-tabs-panel ui-corner-bottom ui-widget-content" aria-hidden="true" style="display: none;"> <div id="aleksi_pins_table_div"> <p> Pins: </p> <table id="aleksi_pins_table"> </table> </div> <div id="aleksi_quizlet_sync"> <!-- <form> <a id="sync_to_quizlet_button" href="javascript:sync_to_quizlet()">Sync with Quizlet</a> <div id="associated_quizlet_set_div"><label for="associated_quizlet_set">Associated Quizlet Set:</label><span id="associated_quizlet_set"></span></div> </form> --> </div> </div> <!-- <span tal:content="morphs" /> --> </div> </div> </div> ';
var aleksi_dialog_html = '<div id="yui3-cssreset"> <div id="aleksi"> <div id="aleksi_dialog"> <ul id="aleksi_tabs"> <li><a id="aleksi_word" href="#aleksi_main" >none</a></li> <li><a href="#aleksi_pins">Pins</a></li> <li id="ui-tab-dialog-close"></li> </ul> <div id="aleksi_main"> <span id="requesting_analysis">Requesting analysis...</span> <span id="analysis_failed">Analysis failed, no results found.</span> <span id="analysis_results"> <p>Dictionary entries:</p> <table id="aleksi_translations_table"> </table> <p>Morphological analysis:</p> <table id="aleksi_morph_tag_tables"> </table> <div class="reference">Powered by <a class="reference" href="http://voikko.puimula.org/">Voikko</a></div> </span> </div> <div id="aleksi_pins"> <div id="aleksi_pins_table_div"> <p>Pins:</p> <table id="aleksi_pins_table"> </table> </div> <div id="aleksi_quizlet_sync"> <!-- <form> <a id="sync_to_quizlet_button" href="javascript:sync_to_quizlet()">Sync with Quizlet</a> <div id="associated_quizlet_set_div"><label for="associated_quizlet_set">Associated Quizlet Set:</label><span id="associated_quizlet_set"></span></div> </form> --> </div> </div> </div> </div> </div>'
var aleksi_navbar_html = '<div id="aleksi_navbar"> <div id="navbar" style="top: 0px;"> <div id="tophiddenbar"> <ul class="left"> <li> <a href="http://localhost/aleksi/"> <b> Aleksi </b> </a> </li> <li> <a href="http://localhost/aleksi/sessions" id="leave_session_button"> <span class="fas-inverse icon-th-large"> </span> <span class="mobile-hide"> Sessions </span> </a> </li> <li> <a href="javascript:update_current_website()" id="update_website_button"> <span class="fas-inverse icon-refresh"> </span> <span class="mobile-hide"> Update Website </span> </a> </li> <!--          <li><a id="open_config_dialog_button">Link behavior</a></li> --> <li> <a id="open_session_dialog_button"> <span class="fas-inverse icon-cog"> </span> <span class="mobile-hide"> Settings </span> </a> </li> </ul> <ul class="right"> <li> <a href="http://localhost/aleksi/logout"> Logout </a> </li> <!-- <li><a id="open_quizlet_dialog_button">Quizlet configuration</a></li> --> </ul> </div> </div> </div>';
var aleksi_session_dialog_html = '<div id="session_dialog" class="ui-dialog-content ui-widget-content"> <form> <!-- title and active website --> <!--          <fieldset class="ui-widget ui-widget-content"> <legend>Session configuration</legend>--> <input autofocus="autofocus" type="hidden"> <div> <label style="padding-right: 5px;"> Session title: </label> </div> <div> <span class="fill"> <input id="session_title_input" name="session_title" type="text" value="Yle Uutiset selkosuomeksi | Yle Uutiset | yle.fi"> </span> </div> <fieldset class="ui-widget ui-widget-content"> <legend> Website Configuration </legend> <div class="controlgroup-vertical-b"> <div> <input id="set_url_option" name="website_setter" type="radio" value="set_url"> <label for="set_url_option" style="padding-right: 5px;"> <div style="display: inline;"> Set Website URL: </div> <!--<option type="radio" id="disable_links_option" value="disable">--> </label> </div> <div class="controlgroup-b ui-state-disabled" id="set_website_url"> <span class="fill"> <input id="website_url_input" name="website_url" type="text" value="https://yle.fi/uutiset/osasto/selkouutiset/"> </span> </div> <div> <input checked="" id="select_website_option" name="website_setter" type="radio" value="select_active"> <label for="select_website_option" style="padding-right: 5px;"> Select Active Website: </label> </div> <div id="website_selector"><select id="website_selectmenu" name="new_website_id" style="display: none;"><optgroup label="https://yle.fi/uutiset/osasto/selkouutiset/" id="61e33933045bcaca14a8ef7750a56a5f"><option id="website_radio_1" value="1" selected="selected">Yle Uutiset selkosuomeksi | Yle Uutiset | yle.fi (2019-05-18 03:24:27.977004)</option></optgroup></select><span tabindex="0" id="website_selectmenu-button" role="combobox" aria-expanded="false" aria-autocomplete="list" aria-owns="website_selectmenu-menu" aria-haspopup="true" class="ui-selectmenu-button ui-selectmenu-button-closed ui-corner-all ui-button ui-widget"><span class="ui-selectmenu-icon ui-icon ui-icon-triangle-1-s"></span><span class="ui-selectmenu-text">Yle Uutiset selkosuomeksi | Yle Uutiset | yle.fi (2019-05-18 03:24:27.977004)</span></span></div> <!-- <label style="padding-right: 5px;">Last retrieved at:</label> <span class="fill" id="website_datetime">2019-05-18 03:24</span> <span class="fill"> <a id="update_website_button" href="javascript:update_website()">Add Webpage to Session</a> </span> --> <div class="controlgroup-vertical-b" style="display: block;"> <div> <label for="lang_selector" style="padding-right: 5px;"> Language </label> </div> <div> <select id="lang_selector" name="lang"> <option id="fi_lang_option" value="fi"> Finnish </option> <option id="sp_lang_option" value="sp"> Spanish </option> </select> </div> <!--<option type="radio" id="disable_links_option" value="disable">--> </div> </div> </fieldset> <fieldset class="ui-widget ui-widget-content"> <legend> Link behavior </legend> <div class="controlgroup-b" id="link_behavior_selector"> <!--<select id="link_behavior" name="link_behavior">--> <div style="display: block;"> <input checked="True" id="disable_links_option" name="link_behavior" type="radio" value="disable"> <label for="disable_links_option" style="padding-right: 5px;"> Disable links </label> <!--<option type="radio" id="disable_links_option" value="disable">--> </div> <div style="display: block;"> <input id="follow_external_links_option" name="link_behavior" type="radio" value="follow_external"> <label for="follow_external_links_option" style="padding-right: 5px;"> Follow links to external URLs </label> <!--<option type="radio" id="follow_external_links_option" value="follow_external"/>--> </div> <div style="display: block;"> <input id="update_session_website_links_option" name="link_behavior" type="radio" value="update_session_website"> <label for="update_session_website_links_option" style="padding-right: 5px;"> Load the linked website into the current session </label> <!--<option type="radio" id="update_session_website_links_option" value="update_session_website"/>--> </div> <!--</select>--> </div> </fieldset> <input id="session_id_input" name="session_id" type="hidden" value="1"> <!-- </fieldset> --> </form> <!-- </div> <div id="quizlet_dialog"> --> <!-- associated Quizlet set --> <div> <a href="http://localhost/aleksi/login/quizlet/" id="quizlet-connect-button" class="ui-button ui-corner-all ui-widget" role="button"> Connect with Quizlet </a> </div> <div id="quizlet" style="display: none;"> <fieldset class="ui-widget ui-widget-content"> <legend> Associated Quizlet study set </legend> <div class="controlgroup-vertical-b"> <div id="quizlet_set_selector"><select id="quizlet_set_selectmenu" name="quizlet_set_id" style="display: none;"><option id="quizlet_set_radio_0" value="0"> -- select a Quizlet set -- </option></select><span tabindex="0" id="quizlet_set_selectmenu-button" role="combobox" aria-expanded="false" aria-autocomplete="list" aria-owns="quizlet_set_selectmenu-menu" aria-haspopup="true" class="ui-selectmenu-button ui-selectmenu-button-closed ui-corner-all ui-button ui-widget"><span class="ui-selectmenu-icon ui-icon ui-icon-triangle-1-s"></span><span class="ui-selectmenu-text"> -- select a Quizlet set -- </span></span></div> </div> <form action="javascript:create_quizlet_set('+"'"+'http://localhost/aleksi/create_quizlet_set'+"'"+')" id="create_quizlet_set_form"> <!-- create new Quizlet set --> <div class="controlgroup-vertical-b"> <div> <label style="padding-right: 5px;"> New Quizlet set title: </label> </div> <div> <span class="fill"> <input id="new_quizlet_set_title_input" name="new_quizlet_set_title" type="text"> </span> </div> <a href="javascript:create_quizlet_set()" id="create_quizlet_set_button" class="ui-button ui-corner-all ui-widget ui-button-disabled ui-state-disabled" role="button"> Create </a> </div> </form> </fieldset> <fieldset class="ui-widget ui-widget-content"> <legend> Sync behavior </legend> <div class="controlgroup-vertical-b"> <!-- <table stlye="border: 0px;"> <tr> <td colspan=2> --> <!-- </td> </tr> <tr> <td> --> <div style="display: block;"> <input id="prune_quizlet_on_sync_input" name="prune_quizlet_on_sync" type="checkbox"> <label for="prune_quizlet_on_sync_input" style="padding-right: 5px;"> Remove extra Quizlet terms on sync </label> </div> <!-- </td> <td style="vertical-align:top"> <span style="display: inline-block; direction: rtl;"> --> <!-- </span> </td> </tr> <tr> <td> --> <div style="display: block;"> <input id="prune_pins_on_sync_input" name="prune_pins_on_sync" type="checkbox"> <label for="prune_pins_on_sync_input" style="padding-right: 5px;"> Remove extra pins on sync </label> </div> <!-- </td> <td style="vertical-align:top"> <span style="display: inline-block; direction: rtl;"> --> <!-- </span> </td> </tr> </table> --> </div> </fieldset> </div> <!-- <fieldset class="ui-widget ui-widget-content"> <legend>Link behavior</legend> <div class="controlgroup-vertical-b" id="link_behavior_selector"> <label style="padding-right: 5px;" for="disable_links_option"> <div style="display: inline;"> Disable links </div> </label> <input name="link_behavior" type="radio" id="disable_links_option" value="disable" checked> <label style="padding-right: 5px;" for="follow_external_links_option"> <div style="display: inline;"> Follow links to external URLs </div> </label> <input name="link_behavior" type="radio" id="follow_external_links_option" value="follow_external"/> <label style="padding-right: 5px;" for="update_session_website_links_option"> <div style="display: inline;"> Load the linked website into the current session </div> </label> <input name="link_behavior" type="radio" id="update_session_website_links_option" value="update_session_website"/> </div> </fieldset> --> <div id="quizlet_connecting" style="display: none;"> <center> <img height="25" src="/aleksi/img/loading_spinner.gif"> </center> </div> <a href="javascript:save_session()" id="save_session_button" class="ui-button ui-corner-all ui-widget" role="button"> Save </a> <a href="javascript:share_session()" id="share_session_button" class="ui-button ui-corner-all ui-widget" role="button"> Share </a> <div id="shared_session" style="display: none;"> <a id="shared_session_link"> Sharable link to session </a> </div> </div>';

$jquery_aleksi('body').append(aleksi_dialog_html);
$jquery_aleksi('body').append(aleksi_navbar_html);
$jquery_aleksi('body').append(aleksi_session_dialog_html);
