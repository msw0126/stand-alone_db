$(function(){
	setTimeout(function(){
		var souid_arr = $("#act-main").attr('souid').split(',');
		if(souid_arr.length<2){
			layer.alert('请选择相应组件进行连接', {
				icon: 2,
				title: '提示'
			});
		};
		//组件load
		$.ajax({
			type:'post',
			url:server+'/atom_act/load',
			data:{
				project_id:proid,
				component_id:$("#act-main").attr('data')
			},
			success:function(data){
				function success(){
					var datas = dataBack(data).detail;
					console.log(datas)
					if(datas==null || datas==""){
						
					}else{
						console.log('88')
						$(".nav-list-act>em").text(datas.reason_code_nvars)
						$("#classification_scores").val(datas.ncores)
					}
					
				}
				backInfo(data,success)
			},
			error: function(data) {
				layer.msg('接口请求失败');
			}
		});
	},10)
	$('.nav-list-act').click(function() {
		$(this).next().toggle(30);
	});
	var _this_text = '';
	$('.nav-list-li>li').click(function() {
		_this_text = $(this).text();
		$(this).parent().parent().find('em').text(_this_text);
		$(this).parent().parent().find('em').css('color', '#858585');
		$(this).parent().hide();

	});
	$(".c-act-save").click(function(){
        var str = $('#classification_scores').val();
        if(str==''){
            $('.c-test-score>p').show();
        }else{

			var reg = /^([1-9]\d*|[0]{1,1})$/;

            if( reg.test(str) ){
                if(str>0){
                    $('.c-test-score>p').hide();
                    var souidArr = $("#act-main").attr('souid').split(',');
                    if($("#act-main").attr('souid')===''){
                        alert('请链接相应组件')
                    }else if(souidArr.length===1&&souidArr[0].substring(0,9)==='AtomLearn'){
                        alert('请链接一份数据')
                    }else{
                        var learnId = '';
                        var inputID = '';
                        for(var i=0;i<souidArr.length;i++){
                            if(souidArr[i].substring(0,9)==='AtomLearn'){
                                learnId = souidArr[i]
                            }else{
                                inputID = souidArr[i]
                            }
                        };
                        $.ajax({
                            type:'post',
                            url:server+'/atom_act/saveInfo?'+timeStamp,
                            data:{
                                project_id:proid,
                                component_id:$("#act-main").attr('data'),
                                atom_learn_id:learnId,
                                input_comp_id:inputID,
                                reason_code_nvars: $(".nav-list-act>em").text(),
                                ncores:$("#classification_scores").val()
                            },
                            success:function(data){
                                function success(){
                                    alertSuccess()
                                };
                                backInfo(data,success)
                            },
                            error: function(data) {
                                layer.msg('接口请求失败');
                            }
                        })
                    }
                }else{
                    $('.c-test-score>p').show();
                }
                //    $('.c-test-score>p').hide();
                // }else{
                //    $('.c-test-score>p').show();
            };
        }


	});
	$(".run").click(function(){
		runParameter($("#act-main").attr('data'))
		$("#runContent").fadeIn()
		$("#shadowBody").show()
	});
    $('#classification_scores').blur(function(){
        var str = $('#classification_scores').val();
        if(str==''){
        	console.log('8888')
        }else{
        	console.log('8888')
        	
        	var reg = /^([1-9]\d*|[0]{1,1})$/;
        
            if( reg.test(str) ){
            	if(str>0){
                    $('.c-test-score>p').hide();
				}else{
                    $('.c-test-score>p').show();
				}
            //    $('.c-test-score>p').hide();
            // }else{
            //    $('.c-test-score>p').show();
           };
        }
        
        
    });
})
