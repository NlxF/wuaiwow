function createCookie(name, value, days) {
    var expires;

    if (days) {
        var date = new Date();
        date.setTime(date.getTime() + (days * 24 * 60 * 60 * 1000));
        expires = "; expires=" + date.toGMTString();
    } else {
        expires = "";
    }
    document.cookie = encodeURIComponent(name) + "=" + encodeURIComponent(value) + expires + "; path=/";
}

function readCookie(name) {
    var nameEQ = encodeURIComponent(name) + "=";
    var ca = document.cookie.split(';');
    for (var i = 0; i < ca.length; i++) {
        var c = ca[i];
        while (c.charAt(0) === ' ')
            c = c.substring(1, c.length);
        if (c.indexOf(nameEQ) === 0)
            return decodeURIComponent(c.substring(nameEQ.length, c.length));
    }
    return null;
}

function eraseCookie(name) {
    createCookie(name, "expires", -1);
}

// $(window).unload(function() {
//     eraseCookie("scount")
// });
// window.addEventListener("beforeunload", function (e) {
//   var confirmationMessage = "\o/";
//
//   (e || window.event).returnValue = confirmationMessage; //Gecko + IE
//   return confirmationMessage;                            //Webkit, Safari, Chrome
// });

$(function(){$("#load-more").click(function()
{
    var load_more_btn = $(this);
    var start_idx = load_more_btn.attr('data-index')
	url = '/blog-load-more/'+ start_idx +'/'+ load_more_btn.attr('data-count');
	$.getJSON($SCRIPT_ROOT + url, {}, function(data) {
	    var blogs = data.result;
        for(var i=0; i<blogs.length; i++)
        {
            var html = '<div class="article-wrapper">'+
                            '<a href="'+ '/wuaiwow/news/'+blogs[i].id+'/'+blogs[i].title +'" itemprop="url">'+
                                '<div class="article-image" style="background-image:url('+ blogs[i].image +')">'+
                                    '<div class="article-image-frame"></div>'+
                                '</div>'+
                                '<div class="article-content" itemprop="blogPost" itemscope="itemscope">'+
                                    '<h2 class="header-2">'+
                                        '<span class="article-title" itemprop="headline">'+
                                            blogs[i].title
                                        +'</span>'+
                                    '</h2>'+
                                    '<span class="clear"><!-- --></span>'+
                                    '<div class="article-summary" itemprop="description">'+blogs[i].content+'</div>'+
                                    '<span class="clear"><!-- --></span>'+
                                '</div>'+
                            '</a>'+
                            '<div class="article-meta">'+
                                '<span class="publish-date" title='+blogs[i].date+'"CST">'+
                                        blogs[i].readable_date
                                +'</span>'+
                            '</div>'+
                            '<span class="clear"><!-- --></span>'+
                        '</div>';
            $("#blog-articles").append(html);
        }
        load_more_btn.attr('data-index', parseInt(start_idx)+blogs.length)
        createCookie("scount", parseInt(start_idx)+blogs.length, 0)
   });
});
})

//刷新
$('body').on('click','.refresh-btn',function(){
    var img = $(this);
    var name = $(this).attr('id')
    var strCls = img.attr("class")
    var pop_toast = function(head, msg, icon){
        var offset = $('#offset-'+name).offset();
                $.toast({
                            heading: head,
                            text: msg,
                            position: {
                                left: offset.left+24.5,
                                top: offset.top+10
                            },
                            icon: icon
                        });
    }
    if (strCls.split(" ")[0]=='stop-img'){
        strCls = strCls.replace('stop-img', 'refresh-img')
        img.attr("class", strCls);
        $.getJSON('/refresh-character', {'id': name}, function(json){
            if (json.status=='Ok'){
                $('#alive-'+name).html(json.alive)
                $('#level-'+name).html(json.level)
                $('#race-'+name).html(json.race)
                $('#job-'+name).html(json.job)
                $('#gender-'+name).html(json.gender)
                $('#money-'+name).html(json.money)
                $('#player_time-'+name).html(json.player_time)
                $('#last_login-'+name).html(json.last_login)
                pop_toast('更新成功', json.msg, 'success')
            }else{
                //pop toast
                pop_toast('出错拉', json.msg, 'error')
            }
            img.attr("class", strCls.replace('refresh-img', 'stop-img'));
        })
        .error(function(jqXHR, textStatus, errorThrown) {
            //pop toast
            pop_toast('出错拉', textStatus, 'error')
            img.attr("class", strCls.replace('refresh-img', 'stop-img'));
        });
    }
})


//$(function(){$('.refresh-btn').click(function()
//{
//    var img = $(this);
//    var name = $(this).attr('id')
//    var strCls = img.attr("class")
//    var pop_toast = function(head, msg, icon){
//        var offset = $('#offset-'+name).offset();
//                $.toast({
//                            heading: head,
//                            text: msg,
//                            position: {
//                                left: offset.left+24.5,
//                                top: offset.top+10
//                            },
//                            icon: icon
//                        });
//    }
//    if (strCls.split(" ")[0]=='stop-img'){
//        strCls = strCls.replace('stop-img', 'refresh-img')
//        img.attr("class", strCls);
//        $.getJSON('/refresh-character', {'id': name}, function(json){
//            if (json.status=='Ok'){
//                $('#alive-'+name).html(json.alive)
//                $('#level-'+name).html(json.level)
//                $('#race-'+name).html(json.race)
//                $('#job-'+name).html(json.job)
//                $('#gender-'+name).html(json.gender)
//                $('#money-'+name).html(json.money)
//                $('#player_time-'+name).html(json.player_time)
//                $('#last_login-'+name).html(json.last_login)
//                pop_toast('更新成功', json.msg, 'success')
//            }else{
//                //pop toast
//                pop_toast('出错拉', json.msg, 'error')
//            }
//            img.attr("class", strCls.replace('refresh-img', 'stop-img'));
//        })
//        .error(function(jqXHR, textStatus, errorThrown) {
//            //pop toast
//            pop_toast('出错拉', textStatus, 'error')
//            img.attr("class", strCls.replace('refresh-img', 'stop-img'));
//        });
//    }
//});
//});
//浮动
$('#myaffix').affix({
    offset: {
      top: 210
    , bottom: function () {
        return (this.bottom = $('#comments').outerHeight(true) + $('#footer').outerHeight(true))
      }
    }
});

$.ajaxSetup({
    beforeSend: function(xhr, settings) {
        if (!/^(GET|HEAD|OPTIONS|TRACE)$/i.test(settings.type)) {
            xhr.setRequestHeader("X-CSRFToken", $('meta[name=csrf-token]').attr('content'))
        }
    }
})
//添加提示语
$('.add-prompt').click(function(){
     var pt_id = $(this).attr('name')
     var tp = $(this).attr('value')
     if ($('#input-'+pt_id).val()){
        $.ajax({
           url: "/admin/add-prompt",
           type: "POST",
           contentType: "application/json",
           data: JSON.stringify({
              id: pt_id,
              type: tp,
              value: $('#input-'+pt_id).val()
           }),
        })
        .done(function (response ) {
            if (response.status=='Ok'){
                var idx = $('#table-' + pt_id + ' tr').size();
	            $("#table-" + pt_id + " > tbody").append('<tr><td style="text-align: center;width:25px;">'+idx+'</td><td style="text-align: center;">'+response.value+'</td><td style="text-align: center;" class="deletetablerow"><div class="glyphicon glyphicon-remove"></div></td></tr>');
            }else{
                $.toast({
                         heading: '出错拉',
                         text: response.msg,
                         position: 'top-center',
                         icon: 'error'
                });
            }
        }).error(function(jqXHR, textStatus, errorThrown){
            $.toast({
                 heading: '出错拉',
                 text: textStatus,
                 position: 'top-center',
                 icon: 'error'
            });
        });
     }
});

//删除提示语
$(".deletetablerow").on("click", function(){
    var btn = $(this)
    $.ajax({
           url: "/admin/del-prompt",
           type: "POST",
           contentType: "application/json",
           data: JSON.stringify({
             id: btn.attr('name'),
             value: btn.prev().html()
           }),
    }).done(function (response ) {
            if (response.status=='Ok'){
                var $killrow = btn.parent('tr');
                $killrow.addClass("danger");
                $killrow.fadeOut(2000, function(){
                    btn.remove();
                });
            }else{
                $.toast({
                         heading: '出错拉',
                         text: response.msg,
                         position: 'top-center',
                         icon: 'error'
                });
            }
        }).error(function(jqXHR, textStatus, errorThrown){
            $.toast({
                 heading: '出错拉',
                 text: textStatus,
                 position: 'top-center',
                 icon: 'error'
            });
        });
});

//提示语活着或死去
$(".dropdown-menu li a").click(function(){
    $(".btn:first-child").html($(this).text()+'<span class="caret" style="margin-top: 0px;"></span>');
    $(".add-prompt").val($(this).parent().val())
});

//新闻
$('#news-file-upload').change(function(){
    readURL(this, '#news-photo');
});

$("form#form-news").submit(function(){
    if ($('#news-title').val() == ""){
        $('#news-title').focus();
        return false;
    }
    for (instance in CKEDITOR.instances) {
        CKEDITOR.instances[instance].updateElement();
    }
    var formData = new FormData($(this)[0]);
    $.ajax({
        url: '/gm/add-news',
        type: 'POST',
        data: formData,
        cache: false,
        contentType: false,
        processData: false,
        success: function (data) {
            if (data.status=='Ok'){
                $('#news-edit-selector').html(' ');
                $.each(data.titles, function(key, value) {
                     $('#news-edit-selector')
                     .append($("<option></option>")
                     .attr("value",key)
                     .text(value));
                });
                $('#news-edit-selector').val(data.selected);

                $.toast({
                 heading: 'Success!',
                 text: data.msg,
                 position: 'top-center',
                 icon: 'Success'
                });
            }else{
                $.toast({
                 heading: '出错拉',
                 text: data.msg,
                 position: 'top-center',
                 icon: 'error'
                });
            }
            $('#news-photo').attr("src", data.photo_url);
            $("#news-file-upload").val('');
            $('#news-content').text('')
        },
        error: function (jqXHR, textStatus, errorThrown) {
            $("#news-file-upload").val('');
            $('#news-content').text('')
        }
    });
    return false;
});

$('#news-edit-selector').on('change', function(ev){
    if($(this).val()!=0){
        $.ajax({
            url: '/gm/get-a-news',
            data: {'title': $(this).val()},
            success: function (data){
                if (data.status == 'Ok'){
                    $('#news-title').val(data.news_title)
                    $('#news-photo').attr("src", data.news_photo)
                    CKEDITOR.instances['news-content'].setData(data.news_content)
                }else{
                    $.toast({
                     heading: '出错拉',
                     text: data.msg,
                     position: 'top-center',
                     icon: 'error'
                    });
                }
            },
            dataType: "json"
        });
    }else{
        $('#news-title').val('')
        $('#news-photo').attr("src", '/static/images/default_title.jpg')
        CKEDITOR.instances['news-content'].setData(' ')
    }
});

//sidebar
$('#sidebar-file-upload').change(function(){
    readURL(this, '#sidebar-photo');
});

$("form#form-sidebar").submit(function(){
    if ($('#sidebar-name').val() == ""){
        $('#sidebar-name').focus();
        return false;
    }
    for (instance in CKEDITOR.instances) {
        CKEDITOR.instances[instance].updateElement();
    }
    var formData = new FormData($(this)[0]);
    $.ajax({
        url: '/admin/add-sidebar',
        type: 'POST',
        data: formData,
        cache: false,
        contentType: false,
        processData: false,
        success: function (data) {
            if (data.status=='Ok'){
                $('#sidebar-edit-selector').html(' ');
                $.each(data.titles, function(key, value) {
                     $('#sidebar-edit-selector')
                     .append($("<option></option>")
                     .attr("value",key)
                     .text(value));
                });
                $('#sidebar-edit-selector').val(1);

                $.toast({heading: 'Success!',text: data.msg,position: 'top-center',icon: 'Success'});
            }else{
                $.toast({heading: '出错拉',text: data.msg,position: 'top-center',icon: 'error'});
            }
            $('#sidebar-photo').attr("src", data.photo_url);
            $("#sidebar-file-upload").val('');
            $('#sidebar-content').text('')
        },
        error: function (jqXHR, textStatus, errorThrown) {
            $("#sidebar-file-upload").val('');
            $('#sidebar-content').text('')
        }
    });
    return false;
});

$('#sidebar-edit-selector').on('change', function(ev){
    if($(this).val()!=0){
        $.ajax({
            url: '/admin/get-a-sidebar',
            data: {'id': parseInt($(this).val(), 10)},
            success: function (data){
                if (data.status == 'Ok'){
                    $('#sidebar-name').val(data.sidebar_name)
                    $('#sidebar-photo').attr("src", data.sidebar_photo)
                    CKEDITOR.instances['sidebar-content'].setData(data.sidebar_content)
                }else{
                    $.toast({heading: '出错拉',text: data.msg,position: 'top-center',icon: 'error'});
                }
            },
            dataType: "json"
        });
    }else{
        $('#sidebar-name').val('')
        $('#sidebar-photo').attr("src", '/static/images/default_title.jpg')
        CKEDITOR.instances['sidebar-content'].setData(' ')
    }
});

$("#role-table").bootstrapTable({
    classes : "table table-bordered table-hover table-striped",//加载的样式
    ajax : "ajaxRequest",//自定义ajax
    search : true,//开启搜索文本框
    showRefresh : true,//开启刷新
    sidePagination : "client",//使用客户端分页
    pagination : "true",//开启分页
    height : 560,
    pageSize : 25,//每页大小
    pageList : [10, 25, 50, 100]//可以选择每页大小
});

function ajaxRequest(params){
    $.ajax({
        type : 'GET',
        url: '/gm/user-role-list/',
        timeout : 20000,
        //data : params.data,
        error: function(xhr,textStatus){
            params.error(' ');
        },
        success  : function(e){
            if(e.status == 'Ok'){
                params.success({
                    total : 1,
                    rows : [{}]
                });
                $("#role-table").bootstrapTable('load', e.rows) //JSON.stringify(e.rows));
            }else{
                params.error(' ');
            }
        }
    });
};

function genDropdown(value, rowData, index) {
    src = '';
    pValue = 0;
    prepend = '';
    for(var p=0; p<rowData.perms.length; p++){
        if(rowData.perms[p] == value){
            pValue = p;
            prepend = rowData.perms[p];
        }
        src += '{value: "'+ rowData.perms[p] +'", text: "'+ rowData.perms[p] +'"},'
    }
    return '<a href="javascript:void(0)" id=permission-'+index+' '+
                'data-pk="101" '+
                'data-type="select" '+
                'data-name="'+rowData.name+'" '+
                'data-value="'+pValue+'"'+
                'data-url="/gm/user-role-list/"'+
                'data-title="修改权限"'+
                'class="editable editable-click">'+
                prepend+
           '</a>'+
           '<script>'+
           '$(' + "'#"+ 'permission-'+ index +"').editable({" +
                                        'source: ['+
                                            src+
                                        '],'+
                                        'validate: {'+
                                            'username: function(v) {if(v == "") return "Required field!"}'+
                                        '},'+
                                        'success: function(response, newValue) {'+
                                            'if(response.status =="Ok") {'+
                                            '    return {newValue: response.newValue};'+
                                            '}else{'+
                                            '    return response.msg;'+
                                            '}'+
                                        '},'+
                                        'error: function(response, newValue) {'+
                                            'if(response.status === 500) {'+
                                            '    return "Service unavailable. Please try later.";'+
                                            '} else {'+
                                            '    return response.responseText;'+
                                            '}'+
                                        '}'+
                                     '});'+
                                  '</script>'
};


$("form#form-permission").submit(function(){
    $.ajax({
        url: '/admin/add-permission/',
        type: 'GET',
        timeout : 2000,
        success: function (data) {
            if (data.status=='Ok'){
                $.toast({
                 heading: 'Success!',
                 text: data.msg,
                 position: 'top-center',
                 icon: 'success'
                });
                location.reload();
            }else{
                $.toast({
                 heading: '出错拉',
                 text: data.msg,
                 position: 'top-center',
                 icon: 'error'
                });
            }
        },
        error: function (jqXHR, textStatus, errorThrown) {
            $.toast({
                 heading: '出错拉',
                 text: "发生了一个错误,请稍后再试",
                 position: 'top-center',
                 icon: 'error'
                });
        }
    });
    return false;
});

$("form#form-roles").submit(function(){
    $role = $('#input-role')
    $select = $('#role-select')
    $label = $('#role-label')
    if($role.val() == ""){
        $role.focus();
        return false;
    }
    if($label.val() == ""){
        $label.focus();
        return false;
    }
    $.ajax({
        url: '/admin/add-role/',
        type: 'POST',
        data: {'newRole': $role.val(), 'newValue': $select.val(), 'newLabel': $label.val()},
        cache: false,
        success: function (data) {
            if (data.status=='Ok'){

                location.reload();
            }else{
                $.toast({
                 heading: '出错拉',
                 text: data.msg,
                 position: 'top-center',
                 icon: 'error'
                });
            }
        },
        error: function (jqXHR, textStatus, errorThrown) {
            $.toast({
                 heading: '出错拉',
                 text: "发生了一个错误,请稍后再试",
                 position: 'top-center',
                 icon: 'error'
                });
        }
    });
    return false;
});

$("form#form-edit-roles").submit(function(){

    $.ajax({
        url: '/admin/change-role-permission/',
        type: 'POST',
        data: {'newRolePerm': $('#form-edit-roles').serialize()},
        cache: false,
        success: function (data) {
            if (data.status=='Ok'){

                location.reload();
            }else{
                $.toast({
                 heading: '出错拉',
                 text: data.msg,
                 position: 'top-center',
                 icon: 'error'
                });
            }
        },
        error: function (jqXHR, textStatus, errorThrown) {
            $.toast({
                 heading: '出错拉',
                 text: "发生了一个错误,请稍后再试",
                 position: 'top-center',
                 icon: 'error'
                });
        }
    });
    return false;
});

function delayUpdateAccount(update_id){
    //Perform Ajax request.
    $('.loadingchars').shCircleLoader({});
    $.ajax({
        url: 'admin/update-account?id='+update_id,
        type: 'GET',
        timeout : 130000,
        success: function(jsonData){
            $('.loadingchars').shCircleLoader('destroy');
            if(jsonData.status=='Ok' && jsonData.characters.length > 0){
                //成功
                var htmlData = ''
                for(var i=0; i<jsonData.characters.length; i++){
                    htmlData += '<div id="offset-'+jsonData.characters[i].name+'" class="span4">'+
                                    '<div class="widget">'+
                                        '<div class="widget-header">'+
                                            '<span class="label label-default span-character-name" style="height:40px">'+
                                                '<label class="label-text-center">'+jsonData.characters[i].name+'</label>'+
                                            '</span>'+
                                            '<img id="'+jsonData.characters[i].name+'" src="" class="stop-img refresh-btn pull-right" alt="刷新中..."/>'+
                                        '</div>'+
                                    '<div class="widget-content alive-'+jsonData.characters[i].alive+'">'+
                                    '<table class="table table-character table-bordered">'+
                                        '<tbody>'+
                                            '<tr>'+
                                                '<td colspan="3" id="alive-'+jsonData.characters[i].name+'" style="text-align: left; ">'+
                                                    jsonData.prompts[0][i]+
                                                '</td>'+
                                            '</tr>'+
                                            '<tr>'+
                                                '<td width= "25px" style="text-align: center; ">等级:</td>'+
                                                '<td width= "25px" id="level-'+jsonData.characters[i].name+'" style="text-align:center; ">'+jsonData.characters[i].level+'</td>'+
                                                '<td style="text-align: center;font-size:10px;">'+
                                                    '<a href="#" id="'+jsonData.characters[i].name+'-'+jsonData.characters[i].level+'" data-type="select" data-pk="1" data-name="'+jsonData.characters[i].name+'" data-url="/gm/promote-character" data-title="快速升级,飞一般的感觉" class="editable editable-click upgrade-level">'+
                                                        jsonData.prompts[1][i]+
                                                    '</a>'+
                                                    '<script>'+
                                                    '$("#'+jsonData.characters[i].name+'-'+jsonData.characters[i].level+'").editable({'+
                                                        'prepend: "'+jsonData.characters[i].level+'级",'+
                                                        'source: ['+(function(level){
                                                                    var levelSrc = "";
                                                                    for(var l=level; l<71; ++l){
                                                                        levelSrc += '{value: '+ l + ', text: "'+ l +'级"},';
                                                                    }
                                                                    return levelSrc;
                                                                })(jsonData.characters[i].level+1)+
                                                        '],'+
                                                        'success: function(response, newValue) {'+
                                                            'if(response.status =="Ok") {'+
                                                                'return response.msg;'+
                                                            '}else{'+
                                                                'return response.msg;'+
                                                                '}'+
                                                        '},'+
                                                        'error: function(response, newValue) {'+
                                                            'if(response.status === 500) {'+
                                                                'return "Service unavailable. Please try later.";'+
                                                            '} else {'+
                                                                'return response.responseText;'+
                                                            '}'+
                                                        '},'+
                                                        'name:"'+jsonData.characters[i].name+'"'+
                                                    '});'+
                                                    '</script>'+
                                                '</td>'+
                                            '</tr>'+
                                            '<tr>'+
                                                '<td width= "25px" style="text-align: center; ">种族:</td>'+
                                                '<td width= "25px" id="race-'+jsonData.characters[i].name+'" style="text-align: center;font-size:10px;">'+jsonData.characters[i].race+'</td>'+
                                                '<td style="text-align: center; font-size:10px;">'+
                                                    '<a href="#" id="'+jsonData.characters[i].name+'-'+jsonData.characters[i].race_id+'" data-name="'+jsonData.characters[i].name+'" data-pk="2" data-name="'+jsonData.characters[i].name+'" data-type="select" data-url="/gm/promote-character" data-title="来一发" class="editable editable-click upgrade-level">'+
                                                        jsonData.prompts[2][i]+
                                                    '</a>'+
                                                    '<script>'+
                                                    '$("#'+jsonData.characters[i].name+'-'+jsonData.characters[i].race_id+'").editable({'+
                                                        'source: ['+(function(races){
                                                                    var rSrc = "";
                                                                    for(var idx=0; idx<races.length; idx++){
                                                                        rSrc += '{value: '+ idx + ', text: "'+ races[idx] +'"},';
                                                                    }
                                                                    return rSrc;
                                                                })(jsonData.races[i])+
                                                        '],'+
                                                        'success: function(response, newValue) {'+
                                                            'if(response.status =="Ok") {'+
                                                                'return response.msg;'+
                                                            '}else{'+
                                                                'return response.msg;'+
                                                            '}'+
                                                        '},'+
                                                        'error: function(response, newValue) {'+
                                                            'if(response.status === 500) {'+
                                                                'return "Service unavailable. Please try later.";'+
                                                            '} else {'+
                                                                'return response.responseText;'+
                                                            '}'+
                                                        '}'+
                                                    '});'+
                                                    '</script>'+
                                                '</td>'+
                                            '</tr>'+
                                            '<tr>'+
                                                '<td width= "25xp" style="text-align: center; ">职业:</td>'+
                                                '<td width= "25px" id="job-'+jsonData.characters[i].name+'" style="text-align: center; ">'+jsonData.characters[i].job+'</td>'+
                                                '<td style="text-align: center; font-size:10px;">'+
                                                    '<a href="#" id="'+jsonData.characters[i].name+'-'+jsonData.characters[i].job+'" class="unknown upgrade-level">'+
                                                        jsonData.prompts[3][i]+
                                                    '</a>'+
                                                '</td>'+
                                            '</tr>'+
                                            '<tr>'+
                                                '<td width= "25px" style="text-align: center; ">性别:</td>'+
                                                '<td width= "25px" id="gender-'+jsonData.characters[i].name+'" style="text-align: center; ">'+jsonData.characters[i].gender+'</td>'+
                                                '<td style="text-align: center; font-size:10px;">'+
                                                    '<a href="#" id="'+jsonData.characters[i].name+'-'+jsonData.characters[i].gender+'" data-type="select" data-pk="4" data-name="'+jsonData.characters[i].name+'" data-url="/gm/promote-character" data-title="变变变" class="editable editable-click upgrade-level">'+
                                                        jsonData.prompts[4][i]+
                                                    '</a>'+
                                                    '<script>'+
                                                    '$("#'+jsonData.characters[i].name+'-'+jsonData.characters[i].gender+'").editable({'+
                                                        'source: ['+
                                                            '{value: 1, text: "当男"},'+
                                                            '{value: 2, text: "当女"}'+
                                                        '],'+
                                                        'success: function(response, newValue) {'+
                                                            'if(response.status =="Ok") {'+
                                                                'return response.msg;'+
                                                            '}else{'+
                                                                'return response.msg;'+
                                                            '}'+
                                                        '},'+
                                                        'error: function(response, newValue) {'+
                                                            'if(response.status === 500) {'+
                                                                'return "Service unavailable. Please try later.";'+
                                                            '} else {'+
                                                                'return response.responseText;'+
                                                            '}'+
                                                        '}'+
                                                    '});'+
                                                    '</script>'+
                                                '</td>'+
                                            '</tr>'+
                                            '<tr>'+
                                                '<td width= "25px" style="text-align: center; ">Money:</td>'+
                                                '<td width= "25px" id="money-'+jsonData.characters[i].name+'" style="text-align: center; ">'+jsonData.characters[i].money+'</td>'+
                                                '<td style="text-align: center; ">'+
                                                    '<a href="#" id="'+jsonData.characters[i].name+'-money" data-pk="5" data-name="'+jsonData.characters[i].name+'" data-type="select" data-title="拼RP" data-url="/gm/promote-character" class="editable editable-click upgrade-level">'+
                                                        jsonData.prompts[5][i]+
                                                    '</a>'+
                                                    '<script>'+
                                                    '$("#'+jsonData.characters[i].name+'-money").editable({'+
                                                        'source: ['+
                                                            '{value: 1, text: "1~9000随机"},'+
                                                            '{value: 2, text: "固定4000"}'+
                                                        '],'+
                                                        'success: function(response, newValue) {'+
                                                            'if(response.status =="Ok") {'+
                                                                'return response.msg;'+
                                                            '}else{'+
                                                                'return response.msg;'+
                                                            '}'+
                                                        '},'+
                                                        'error: function(response, newValue) {'+
                                                            'if(response.status === 500) {'+
                                                                'return "Service unavailable. Please try later.";'+
                                                            '} else {'+
                                                                'return response.responseText;'+
                                                            '}'+
                                                        '},'+
                                                        'name:"'+jsonData.characters[i].name+'"'+
                                                    '});'+
                                                    '</script>'+
                                                '</td>'+
                                            '</tr>'+
                                            '<tr>'+
                                                '<td colspan="3">'+
                                                    '<span>游戏总时间:</span><span id="player_time-'+jsonData.characters[i].name+'">'+jsonData.characters[i].played_time+'</span>'+
                                                    '<br/>'+
                                                    '<span>上次登录时间:</span><span id="last_login-'+jsonData.characters[i].name+'">'+jsonData.characters[i].last_login+'</span><a href="/user/change-password"> 有疑问?立即修改密码</a>'+
                                                '</td>'+
                                            '</tr>'+
                                        '</tbody>'+
                                    '</table>'+
                                    '</div> <!-- /widget-content -->'+
                                '</div> <!-- /widget -->'+
                                '</div> <!-- /span4 -->'
                }
                $('.click-udtacntchar').removeAttr("disabled");
                $('.click-udtacntchar').text("刷新");
                $('.udtacntchar').html(htmlData);
            }else{
                $('.click-udtacntchar').removeAttr("disabled");
                $('.click-udtacntchar').text(jsonData.msg+',点击重新刷新');
            }
        },
        error: function (xhr, ajaxOptions, thrownError) {
            $('.loadingchars').shCircleLoader('destroy');
            $('.click-udtacntchar').removeAttr("disabled");
            if(ajaxOptions=='timeout')
                $('.click-udtacntchar').text("更新超时,点击重新刷新");
            else if(ajaxOptions=='error')
                $('.click-udtacntchar').text("服务器内部错误,稍后重试");
        }
    });
};

$('.click-udtacntchar').click(function(){
    $('.click-udtacntchar').attr("disabled", "disabled");
    $('.click-udtacntchar').text("正在刷新...");
    delayUpdateAccount((Math.random()+1).toString(36).substr(2, 18))
});

function readURL(input, tag) {
    if (input.files && input.files[0]) {
        var reader = new FileReader();
        reader.onload = function (e) {
            $(tag).attr('src', e.target.result);
        }
        reader.readAsDataURL(input.files[0]);
    }
    else
    {
        /*var sFilter='filter:progid:DXImageTransform.Microsoft.AlphaImageLoader(sizingMethod=scale,src="';
        file.select();
        var src = document.selection.createRange().text,
            mysrc = sFilter+src;
        porImg.filters.item('DXImageTransform.Microsoft.AlphaImageLoader').src = src;
       // porImg.attr({mysrc:"",class:"aaa"});
       */
        var ieImageDom = document.createElement("div");
        var proIeImageDom = document.createElement("div");
        $(ieImageDom).css({
            float: 'left',
            position: 'relative',
            overflow: 'hidden',
            width: '100px',
            height: '100px'
        }).attr({"id":"view"});
        $(proIeImageDom).attr({"id":"biuuu"});
        porImg.parent().prepend(proIeImageDom);
        porImg.remove();
        viewImg.parent().append(ieImageDom);
        viewImg.remove();
        file.select();
        path = document.selection.createRange().text;
        $(ieImageDom).css({"filter": "progid:DXImageTransform.Microsoft.AlphaImageLoader(enabled='true',sizingMethod='scale',src=\"" + path + "\")"});
        $(proIeImageDom).css({"filter": "progid:DXImageTransform.Microsoft.AlphaImageLoader(enabled='true',sizingMethod='scale',src=\"" + path + "\")"});
   // .style.filter = "progid:DXImageTransform.Microsoft.AlphaImageLoader(enabled='true',sizingMethod='scale',src=\"" + path + "\")";//Ê¹ÓÃÂË¾µÐ§¹û
        /*var imagePath = file.value;
        porImg.attr({
            src : "file://" + imagePath
        });*/
    }
}

$(function () { $("[data-toggle='tooltip']").tooltip(); });

function base64ToBlob(base64, mime)
{
    mime = mime || '';
    var sliceSize = 1024;
    var byteChars = window.atob(base64);
    var byteArrays = [];

    for (var offset = 0, len = byteChars.length; offset < len; offset += sliceSize) {
        var slice = byteChars.slice(offset, offset + sliceSize);
        var byteNumbers = new Array(slice.length);
        for (var i = 0; i < slice.length; i++) {
            byteNumbers[i] = slice.charCodeAt(i);
        }
        var byteArray = new Uint8Array(byteNumbers);
        byteArrays.push(byteArray);
    }
    return new Blob(byteArrays, {type: mime});
}