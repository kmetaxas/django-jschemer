$(document).ready(function(){

    function jschemer_get_postRender_funcion(element){
        // Genarate a function because defining a function in a loop inside
        // postRender definition is a closure and  references the same variable. We don't want that
        return function(control){
            window.controls[element.attr("id")] = control;
        }
    }

    function jschemer_initialize_alpaca_for_widgets(){
        window.controls = {}; // All controls associated with hidden form ID as key
        $.alpaca.setDefaultLocale("el_GR");
        var elements = $('[data-alpaca="true"]');
        for(var i=0;i<elements.length;i++){

            var element = $(elements[i]);
            var schema = JSON.parse( element.attr("data-schemajson")); // TODO check for errors
            var option_str = element.attr("data-alpacaoptions");
            if(!option_str){
                var options = {};
            }
            else{
                var options = JSON.parse(option_str);
            }

            var innerDivId = "alpacaform_"+element.attr('id');
            element.after('<div id="'+innerDivId+'"</div>');
            $("#"+innerDivId).alpaca( {
                "schema":schema,
                "options":options,
                "postRender":jschemer_get_postRender_funcion(element),
            });
        }
        var jschemer_serialize_controls_to_hidden_fields = function(){
            for(key in window.controls){
                var control = window.controls[key];
                $("#"+key).val( JSON.stringify(control.getValue()));
            }
        }
        $.jschemer_serialize_controls_to_hidden_fields =jschemer_serialize_controls_to_hidden_fields;

        $("form").submit(function(e){
            jschemer_serialize_controls_to_hidden_fields();
        });
    }

    jschemer_initialize_alpaca_for_widgets();
});

