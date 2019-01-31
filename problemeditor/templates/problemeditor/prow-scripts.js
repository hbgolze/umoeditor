/*
      <select id="topic_{{p.pk}}" class="change-topic form-control form-control-sm mb-1">
        <option value="Algebra" {% if p.topic == "Algebra" %}selected{% endif %}>Algebra
        </option>
      </select>
      <select id="addtolist_{{p.pk}}" class="add-to-list form-control form-control-sm mb-1">
	<option value="" disabled selected>Choose a List</option>
	{% for mklist in mklists %}
	<option value="{{mklist.pk}}">{{mklist.name}}</option>
	{% endfor %}
*/

function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = jQuery.trim(cookies[i]);
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

var csrftoken = getCookie('csrftoken');

function csrfSafeMethod(method) {
    // these HTTP methods do not require CSRF protection
    return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
}

$.ajaxSetup({
	beforeSend: function(xhr, settings) {
	    if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
		xhr.setRequestHeader("X-CSRFToken", csrftoken);
	    }
	},
	    });

$(document).on('change',"select.diff-select",function(e) {
	
	var pk = $(this).attr("id").split('_')[1];
	$.ajax({
		type: 'POST',
		    url: '/ajax/change-difficulty/',
		    data: 'pk='+pk+'&diff='+$(this).val(),
		    dataType: 'json',
		    success: function(data) {
		    
		    $("#difficulty-changed").show();
		    setTimeout(function() {
			    $("#difficulty-changed").fadeOut();
			},5000);
		    
		    
		}
	    });
    });

$(document).on('change',"select.status-select",function(e) {
	
	var pk = $(this).attr("id").split('_')[1];
	$.ajax({
		type: 'POST',
		    url: '/ajax/change-status/',
		    data: 'pk='+pk+'&stat='+$(this).val(),
		    dataType: 'json',
		    success: function(result) {
		    {% if not mocklist %}
		    $("#problem-card_"+pk).remove();
		    if ($("#typetopic-"+result['subtract-here']).children().length == 1) {
			$("#empty-message-"+result['subtract-here']).show();
		    }
		    if ($("#typetopic-"+result['add-here']).children().length == 1) {
			$("#empty-message-"+result['add-here']).hide();
		    }
		    $("#typetopic-"+result['add-here']).append(result['prob-card']);
		    MathJax.Hub.Queue(["Typeset",MathJax.Hub,"problem-card_"+pk]);
		    {% endif %}
		      $("#status-changed").show();
		      setTimeout(function() {
			    $("#status-changed").fadeOut();
			  },5000);
		    
		    
		}
	    });
    });

$(document).on('change',"select.change-topic",function(e) {
	
	var pk = $(this).attr("id").split('_')[1];
	$.ajax({
		type: 'POST',
		    url: '/ajax/change-topic/',
		    data: 'pk='+pk+'&topic='+$(this).val(),
		    dataType: 'json',
		    success: function(result) {
		    {% if not mocklist %}
		    $("#problem-card_"+pk).remove();
		    if ($("#typetopic-"+result['subtract-here']).children().length == 1) {
			$("#empty-message-"+result['subtract-here']).show();
		    }
		    if ($("#typetopic-"+result['add-here']).children().length == 1) {
			$("#empty-message-"+result['add-here']).hide();
		    }
		  
		    $("#typetopic-"+result['add-here']).append(result['prob-card']);
		    MathJax.Hub.Queue(["Typeset",MathJax.Hub,"problem-card_"+pk]);
		    {% endif %}
		      $("#topic-changed").show();
		      setTimeout(function() {
			    $("#topic-changed").fadeOut();
			  },5000);
		    
		    
		}
	    });
    });
$(document).on('change',"select.add-to-list",function(e) {
	
	var pk = $(this).attr("id").split('_')[1];
	$.ajax({
		type: 'POST',
		    url: '/ajax/add-to-list/',
		    data: 'pk='+pk+'&list_pk='+$(this).val(),
		    dataType: 'json',
		    success: function(result) {
		    if (result['status'] == 1) {
		      $("#added-to-list").show();
		      setTimeout(function() {
			    $("#added-to-list").fadeOut();
			  },5000);
		    }
		    if (result['status'] == 0) {
		      $("#prev-added-to-list").show();
		      setTimeout(function() {
			    $("#prev-added-to-list").fadeOut();
			  },5000);
		    }
		    
		    
		    
		}
	    });
    });
{% if mocklist %}
$(document).on('click',".remove-from-mocklist",function(e) {
	
	var pk = $(this).attr("id").split('_')[1];
	var ppk = $(this).attr("id").split('_')[2];
	$.ajax({
		type: 'POST',
		    url: '/ajax/remove-from-list/',
		    data: 'pk='+pk+'&ppk='+ppk,
		    dataType: 'json',
		    success: function(result) {
		    $("#problem-card_"+ppk).remove();
		    
		    
		}
	    });
    });
{% endif %}
$(document).on('click','.solution-link',function(e) {
	var pk = $(this).attr("id").split('_')[1];
	$.ajax({
		type: 'GET',
		    url: '/ajax/load-solutions/',
		    data: 'pk='+pk,
		    dataType: 'json',
		    success: function(result) {		    
		    $('#solution-placeholder').html(result['modal-html']);
		    MathJax.Hub.Queue(["Typeset",MathJax.Hub,"solution-placeholder"]);
		    $('#solution-placeholder').modal("show");
		}
	    });
    });

$(document).on('click','.new-solution-link',function(e) {
	var pk = $(this).attr("id").split('_')[1];
	$.ajax({
		type: 'GET',
		    url: '/ajax/new-solution/',
		    data: 'pk='+pk,
		    dataType: 'json',
		    success: function(result) {		    
		    $('#solution-placeholder').html(result['modal-html']);
		    MathJax.Hub.Queue(["Typeset",MathJax.Hub,"solution-placeholder"]);		    
		    $("#solution-placeholder").modal("show");
		}
	    });
	
    });
$(document).on('submit',"#new-solution-form",function(event) {
	event.preventDefault();
	$.ajax({
		type: 'POST',
		    url: '/ajax/save-new-solution/',
		    data: $(this).serialize(),
		    dataType: 'json',
		    success: function(result) {
		    $("#solution-link_"+result['pk']).text("Solutions ("+result['sol_count']+")");
		    $("#solution-placeholder").hide();
		    $("[data-dismiss=modal]").trigger({ type: "click" });
		}
	    });
	return false;
    });

$(document).on("click","#preview-latex-button", function(e) {
	sol_text = $("#codetext[name=new_solution_text]").val().trim();
	sol_text = '<p>'+sol_text.replace(/</g,' < ').replace(/(?:\r\n|\r|\n)/g,'<br/>')+'</p>';

	sol_text = replace_enumitem(sol_text);
	sol_text = replace_center(sol_text);

	$("#preview-latex").html(sol_text);
	$("#preview-latex").show();
	MathJax.Hub.Queue(["Typeset",MathJax.Hub,"preview-latex"]);
    });

$(document).on('click',".pre-delete-sol-link",function(e) {
	var sol_id = $(this).attr('id').split('_')[1];
	$("#confirmdelete_"+sol_id).show();
    });
$(document).on('click',".no-delete-sol-link",function(e) {
	var sol_id = $(this).attr('id').split('_')[1];
	$("#confirmdelete_"+sol_id).hide();
    });

$(document).on('click',".delete-sol-link",function(event) {
	event.preventDefault();
	var sol_id = $(this).attr('id').split('_')[2];
	var prob_id = $(this).attr('id').split('_')[1];
	$.ajax({
		type: 'POST',
		    url: '/ajax/delete-solution/',
		    data: "pk="+prob_id+"&spk="+sol_id,
		    dataType: 'json',
		    success: function(result) {
		    if (result['deleted']==1) {
			$("#solution-link_"+prob_id).text("Solutions ("+result['sol_count']+")");
			$("#num_solutions-"+prob_id).html(result['sol_count']);
			$("#sol_"+sol_id).remove();
			if ($("#all_solutions > div").length == 0) {
			    $("#no-solutions").show();
			}
		    }
		}
	    });
	return false;
    });


$(document).on('click',".edit-primitive-preview-link",function(event) {
	event.preventDefault();
	var sol_id = $(this).attr('id').split('_')[2];
	var prob_id = $(this).attr('id').split('_')[1];
	var prob_label = $(this).attr('id').split('_')[3];
	sol_text = $("#editsolplaceholder_"+sol_id+" #codetext[name=solution_text]").val().trim();


	sol_text = '<p>'+sol_text.replace(/</g,' < ').replace(/(?:\r\n|\r|\n)/g,'<br/>')+'</p>';

	sol_text = replace_images(sol_text,prob_label);
	sol_text = replace_enumitem(sol_text);
	sol_text = replace_center(sol_text);

	$("#preview_soltext_"+sol_id).html(sol_text);
	$("#soltext_"+sol_id).hide();
	$("#preview_soltext_"+sol_id).show();
	MathJax.Hub.Queue(["Typeset",MathJax.Hub,"preview_soltext_"+sol_id]);
    });

$(document).on('click',".cancel-edit-sol-link",function(event) {
	event.preventDefault();
	var sol_id = $(this).attr('id').split('_')[2];
	var prob_id = $(this).attr('id').split('_')[1];
	$("#editsolplaceholder_"+sol_id).empty()
	    $("#soltext_"+sol_id).show();
	$("#editsol_"+prob_id+"_"+sol_id).show();
    });

$(document).on('click',".edit-sol-link",function(event) {
	event.preventDefault();
	var sol_id = $(this).attr('id').split('_')[2];
	var prob_id = $(this).attr('id').split('_')[1];
	$.ajax({
		type: 'POST',
		    url: '/ajax/load-edit-sol/',
		    data: "pk="+prob_id+"&spk="+sol_id,
		    dataType: 'json',
		    success: function(result) {
		    $("#editsol_"+prob_id+"_"+sol_id).hide();
		    $("#editsolplaceholder_"+sol_id).html(result['sol_form']);
		    window.location ="#editsolplaceholder_"+sol_id;
		}
	    });
	return false;
    });

$(document).on('click',".save-sol-link",function(event) {
	event.preventDefault();
	var sol_id = $(this).attr('id').split('_')[2];
	var prob_id = $(this).attr('id').split('_')[1];
	$.ajax({
		type: 'POST',
		    url: '/ajax/save-sol/',
		    data: "pk="+prob_id+"&spk="+sol_id+"&solution_text="+encodeURIComponent($("#editsolplaceholder_"+sol_id+" #codetext").val()),
		    dataType: 'json',
		    success: function(result) {
		    $("#soltext_"+sol_id).html(result['sol_text']);
		    MathJax.Hub.Queue(["Typeset",MathJax.Hub,"soltext_"+sol_id]);
		    $("#editsolplaceholder_"+sol_id).empty()
			d = new Date();
		    $("#soltext_"+sol_id+" img").each(function(e) {
			    url = $(this).attr("src");
			    $(this).attr("src",url+"?"+d.getTime());
			});
		    $("#editsol_"+prob_id+"_"+sol_id).show();
		    $("#soltext_"+sol_id).show();

		}
	    });
	return false;
    });
$(document).on('click',".edit-primitive-preview-link",function(event) {
	event.preventDefault();
	var sol_id = $(this).attr('id').split('_')[2];
	var prob_id = $(this).attr('id').split('_')[1];
	var prob_label = $(this).attr('id').split('_')[3];
	sol_text = $("#editsolplaceholder_"+sol_id+" #codetext[name=solution_text]").val().trim();


	sol_text = '<p>'+sol_text.replace(/</g,' < ').replace(/(?:\r\n|\r|\n)/g,'<br/>')+'</p>';

	sol_text = replace_images(sol_text,prob_label);
	sol_text = replace_enumitem(sol_text);
	sol_text = replace_center(sol_text);

	$("#preview_soltext_"+sol_id).html(sol_text);
	$("#soltext_"+sol_id).hide();
	$("#preview_soltext_"+sol_id).show();
	MathJax.Hub.Queue(["Typeset",MathJax.Hub,"preview_soltext_"+sol_id]);
    });
{% if not mocklist %}
$(document).on('click','.add-problem-link',function(e) {
	$.ajax({
		type: 'GET',
		    url: '/ajax/add-problem/',
		    dataType: 'json',
		    success: function(result) {
		    $('#add-problem-placeholder').html(result['modal-html']);
		    $("#add-problem-placeholder").modal("show");
		}
	    });
	
    });

$(document).on('submit',"#add-problem-form",function(event) {
	event.preventDefault();
	$.ajax({
		type: 'POST',
		    url: '/ajax/save-new-problem/',
		    data: $(this).serialize(),
		    dataType: 'json',
		    success: function(result) {
		    if ($("#typetopic-"+result['add-here']).children().length == 1) {
			$("#empty-message-"+result['add-here']).hide();
		    }
		    $("#typetopic-"+result['add-here']).append(result['prob-card']);
		    MathJax.Hub.Queue(["Typeset",MathJax.Hub,"problem-card_"+result['pk']]);

		    $("#add-problem-placeholder").hide();
		    $("[data-dismiss=modal]").trigger({ type: "click" });
		    location.href = "#problem-card_"+result['pk']; 
		    $("#problem-added").show();

		    setTimeout(function() {
			    $("#problem-added").fadeOut();
			},5000);
		    
		}
	    });
	return false;
    });

$(document).on("click","#add-problem-preview-link", function(e) {
	p_text = $("#codetext[name=problem_text]").val().trim();//may need editing if a second 'edit latex' button is added
	p_text = '<p>'+p_text.replace(/</g,' < ').replace(/(?:\r\n|\r|\n)/g,'<br/>')+'</p>';

	p_text = replace_enumitem(p_text);
	p_text = replace_center(p_text);

	$("#add-problem-preview").html(p_text);
	$("#add-problem-preview").show();
	MathJax.Hub.Queue(["Typeset",MathJax.Hub,"add-problem-preview"]);
    });
{% endif %}
//solution-placeholder"