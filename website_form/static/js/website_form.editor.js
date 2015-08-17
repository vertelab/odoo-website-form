$(document).ready(function() {
    "use strict";

    var website = openerp.website;
    var _t = openerp._t;

    website.EditorBarContent.include({
        new_form_post: function() {
            website.prompt({
                id: "editor_new_form",
                window_title: _t("New Form"),
                select: _t("Select Model"),
                init: function (field) {
                    var $group = this.$dialog.find("div.form-group");
                    $group.removeClass("mb0");
                    var $pre = $(
                        '<div class="form-group ">'+
                            '<label class="col-sm-3 control-label" for="form_name""/>'+
                            '<div class="col-sm-9"><input type="text" id="form_name" name="form_name" required="required"/></div> '+
                            + '</div>'
                        );
                    $pre.find('label').prepend(_t("Form Title:"));
                    $group.before($pre);
                    var $add = $('<div class="form-group ">'+
                            '<label class="col-sm-3 control-label" id="thanks" for="thanks_url"/>'+
                            '<div class="col-sm-9"><input type="text" id="thanks_url" name="thanks_url" value="/page/website_form.thank_you" /></div> '+
                            '</div>' +
                        '<div class="form-group mb0">'+
                            '<label class="col-sm-offset-3 col-sm-9 text-left" id="add_menu" >'+
                            '    <input type="checkbox" checked="checked" required="required"/></label> '+

                        '</div>'
                        );
                    $add.find('label[id="thanks"]').append(_t("Thanks Url: "));
                    $add.find('label[id="add_menu"]').append(' ' + _t("Add page in menu"));

                    $group.after($add);
                    return website.session.model('ir.model')
                            .call('name_search', [], { context: website.get_context() });
                }
                
                
             }).then(function (val,field,$dialog) {
                console.log('val:',val,'field:',field,'dialog:',$dialog);
                if (val) {
                    var title = $dialog.find('input[name="form_name"]');
                    console.log(title);
                    console.log(title.val());
                    var url = '/form/' + encodeURIComponent(title.val()) + '/add?model_id=' + val;
                    if ($dialog.find('input[type="checkbox"]').is(':checked')) url +="&add_menu=1";
                    if ($dialog.find('input[name="thanks_template"]').val()) url +="&thanks_template=%s" % $dialog.find('input[name="thanks_template"]').val();
                    document.location = url;
                }
            });
            
        },
        new_form: function() {
            website.prompt({
                id: "editor_new_page",
                window_title: _t("New Page"),
                input: _t("Page Title"),
                init: function () {
                    var $group = this.$dialog.find("div.form-group");
                    $group.removeClass("mb0");

                    var $add = $(
                        '<div class="form-group mb0">'+
                            '<label class="col-sm-offset-3 col-sm-9 text-left">'+
                            '    <input type="checkbox" checked="checked" required="required"/> '+
                            '</label>'+
                        '</div>');
                    $add.find('label').append(_t("Add page in menu"));
                    $group.after($add);
                }
            }).then(function (val, field, $dialog) {
                if (val) {
                    var url = '/website/add/' + encodeURIComponent(val);
                    if ($dialog.find('input[type="checkbox"]').is(':checked')) url +="?add_menu=1";
                    document.location = url;
                }
            });
        },
        

        
        
        
    });
    if ($('.website_form').length) {
        website.EditorBar.include({
            edit: function () {
                var self = this;
                $('.popover').remove();
                this._super();
                var vHeight = $(window).height();
                $('body').on('click','#change_cover',_.bind(this.change_bg, self.rte.editor, vHeight));
                $('body').on('click', '#clear_cover',_.bind(this.clean_bg, self.rte.editor, vHeight));
            },
            save : function() {
                var res = this._super();
                if ($('.cover').length) {
                    openerp.jsonRpc("/form/change_background", 'call', {
                        'post_id' : $('#blog_post_name').attr('data-oe-id'),
                        'image' : $('.cover').css('background-image').replace(/url\(|\)|"|'/g,''),
                    });
                }
                return res;
            },
            clean_bg : function(vHeight) {
                $('.js_fullheight').css({"background-image":'none', 'min-height': vHeight});
            },
            change_bg : function(vHeight) {
                var self  = this;
                var element = new CKEDITOR.dom.element(self.element.find('.cover-storage').$[0]);
                var editor  = new website.editor.MediaDialog(self, element);
                $(document.body).on('media-saved', self, function (o) {
                    var url = $('.cover-storage').attr('src');
                    $('.js_fullheight').css({"background-image": !_.isUndefined(url) ? 'url(' + url + ')' : "", 'min-height': vHeight});
                    $('.cover-storage').hide();
                });
                editor.appendTo('body');
            },
        });
    }
});
