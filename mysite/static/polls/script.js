$(document).ready(function(){
    $('#avatar').change(function(){
        let file = this.files[0];
        console.log(file);
        let reader = new FileReader();
        let allowedTypes = ['image/jpeg', 'image/png', 'image/jpg'];
        if (allowedTypes.indexOf(file.type) == -1) {
            alert('Invalid file type. Please upload a valid image file.');
            return false;
        }
        reader.onload = function(e) {
            $('#preview').attr('src', e.target.result);
        };
        $('#editProfileSubmitBtn').prop('disabled', false);
        reader.readAsDataURL(file);
    });

    
    $("#editProfileSubmitBtn").click(function() {
        $("#editProfileForm").submit();
    });

    // $("#createGroupModal").on('hidden.bs.modal', function () {
    //     $(this).find('form').trigger('reset');
    //     $(this).find('form').find('input[type="text"]').val('');
    //     $(this).find('form').find('textarea').val('');
    //     $(this).find('form').find('input').removeClass('is-invalid');
    //     $(this).find('form').find('.invalid-feedback').remove();
        
    // });

    let initialFormState = $('#editProfileForm').serialize();

    $("#editProfileForm").on("input",function() {
        checkFormChanges(initialFormState);
    })
    $("#markdownx-tabs button").click(function(e) {
        e.preventDefault()
        $(this).tab('show')
    })

    $("#deleteUserBtn").on("click",function() {
        $.ajax({
            url: "/polls/delete-user/",
            type: "POST",
            headers:{
                'X-CSRFToken': $('input[name=csrfmiddlewaretoken]').val()
            },
            success: function(response) {
                if (response.success) {
                    window.location.href = response.redirect;
                }  
            },
            error: function() {
                console.log("Error");
            }
            
        })
    })
    $("#postCommentBtn").on("click", function(){
        let comment = $("#CommentField").val();
        if(!comment) {
            return;
        }
        $("#CommentField").val("");
        $.ajax({
            url: window.location.href + "post-comment/",
            type: "POST",
            headers:{
                'X-CSRFToken': $('input[name=csrfmiddlewaretoken]').val()
            },
            data: {
                comment: comment
            },
            success: function(response) {
                if(response) {
                    $("#commentContainer").append(response);
                    let commentCount = parseInt($("#commentCount").text())
                    $("#commentCount").text(`${commentCount + 1} Comments`);
                }               
            },
            error: function(xhr, status, error) {
                if(xhr.status === 401) {
                    let response = JSON.parse(xhr.responseText);
                    window.location.href = response.redirect;
                }
                else{
                    console.log(error);
                }
            }
            
        })
    })
    $('#deleteBlogBtn').click(function(event) {
        event.preventDefault();
        $.ajax({
            url: window.location.href + "delete/",
            type: "POST",
            headers:{
                'X-CSRFToken': $('input[name=csrfmiddlewaretoken]').val()
            },
            success: function(response) {
                if (response?.success) {
                    window.location.href = response.redirect;
                }  
            },
            error: function(xhr, status, error) {
                if(xhr.status === 401) {
                    let response = JSON.parse(xhr.responseText);
                    window.location.href = response.redirect;
                    return;
                }
                console.log("Error");
            }
            
        })
    })
});

function checkFormChanges(initialFormState) {
    let currentFormState = $("#editProfileForm").serialize();
    if (currentFormState === initialFormState) {
        console.log("same");
        $('#editProfileSubmitBtn').prop('disabled', true);
    } else {
        console.log("different");
        $('#editProfileSubmitBtn').prop('disabled', false);
    }
}

function likeBlog(event, blogId) {
    event.stopPropagation();
    const blogDiv = $(`div[data-blog-id="${blogId}"]`);
    let dislikeIcon = blogDiv.find(".fa-thumbs-down");
    let likeIcon = event.currentTarget;
    let POST_URL = window.location.href;
    if(POST_URL.endsWith(`polls/post/${blogId}/`)) {
        POST_URL += "like/"; 
    } else {
        POST_URL = `/polls/post/${blogId}/like/`;
    }
    
    $.ajax({
        url: POST_URL,
        type: "POST",
        headers:{
            'X-CSRFToken': $('input[name=csrfmiddlewaretoken]').val()
        },
        success: function(response) {
            if(response) {
                if(response?.success){
                    if($(likeIcon).data("prefix") === "far"){
                    $(likeIcon).attr("data-prefix", "fas");
                        $(dislikeIcon).attr("data-prefix", "far");
                    } else if($(likeIcon).data("prefix") === "fas") {
                        $(likeIcon).attr("data-prefix", "far");
                    }
                    $(blogDiv).find(`#likeCount`).text(response.likes);
                    $(blogDiv).find(`#dislikeCount`).text(response.dislikes);
                    return;
                }   
            }
                        
        },
        error: function(xhr, status, error) {
            if(xhr.status === 401) {
                let response = JSON.parse(xhr.responseText);
                window.location.href = response.redirect;
            }
            else{
                console.log(error);
            }
        }
        
    })
}

function dislikeBlog(event, blogId) {
    event.stopPropagation();
    const blogDiv = $(`div[data-blog-id="${blogId}"]`);
    let dislikeIcon = event.currentTarget;
    let likeIcon = blogDiv.find(".fa-thumbs-up");
    let POST_URL = window.location.href;
    if(POST_URL.endsWith(`polls/post/${blogId}/`)) {
        POST_URL += "dislike/";
    } else {
        POST_URL = `/polls/post/${blogId}/dislike/`;
    }
    
    $.ajax({
        url: POST_URL,
        type: "POST",
        headers:{
            'X-CSRFToken': $('input[name=csrfmiddlewaretoken]').val()
        },
        success: function(response) {
            if(response) {
                if(response.success){
                    if($(dislikeIcon).data("prefix") === "far"){
                        $(dislikeIcon).attr("data-prefix", "fas");
                        $(likeIcon).attr("data-prefix", "far");
                    } else if($(dislikeIcon).data("prefix") === "fas") {
                        $(likeIcon).attr("data-prefix", "far");
                    }
                    $(blogDiv).find(`#likeCount`).text(response.likes);
                    $(blogDiv).find(`#dislikeCount`).text(response.dislikes);
                    return;
                }
                window.location.href = response.redirect;
            }               
        },
        error: function(xhr, status, error) {
            if(xhr.status === 401) {
                let response = JSON.parse(xhr.responseText);
                window.location.href = response.redirect;
            }
            else{
                console.log(error);
            }
        }
        
    })
}

function likeComment(event, commentId) {
    event.stopPropagation();
    const commentDiv = $(`div[data-comment-id="${commentId}"]`);
    let dislikeIcon = commentDiv.find(".fa-thumbs-down");
    let likeIcon = event.currentTarget;
    let POST_URL = `comment/${commentId}/like/`;
    
    $.ajax({
        url: POST_URL,
        type: "POST",
        headers:{
            'X-CSRFToken': $('input[name=csrfmiddlewaretoken]').val()
        },
        success: function(response) {
            if(response) {
                if(response?.success){
                    if($(likeIcon).data("prefix") === "far"){   
                        $(likeIcon).attr("data-prefix", "fas");
                        $(dislikeIcon).attr("data-prefix", "far");
                    } else if($(likeIcon).data("prefix") === "fas") {
                        $(likeIcon).attr("data-prefix", "far");
                    }
                    $(commentDiv).find(`#likeCount`).text(response.likes);
                    $(commentDiv).find(`#dislikeCount`).text(response.dislikes);
                    return;
                }   
            }
                        
        },
        error: function(xhr, status, error) {
            if(xhr.status === 401) {
                let response = JSON.parse(xhr.responseText);
                window.location.href = response.redirect;
            }
            else{
                console.log(error);
            }
        }
        
    })
}

function dislikeComment(event, commentId) {
    event.stopPropagation();
    const commentDiv = $(`div[data-comment-id="${commentId}"]`);
    let dislikeIcon = event.currentTarget;
    let likeIcon = commentDiv.find(".fa-thumbs-up");
    let POST_URL = `comment/${commentId}/dislike/`;
    
    $.ajax({
        url: POST_URL,
        type: "POST",
        headers:{
            'X-CSRFToken': $('input[name=csrfmiddlewaretoken]').val()
        },
        success: function(response) {
            if(response) {
                if(response?.success){
                    if($(dislikeIcon).data("prefix") === "far"){
                        $(dislikeIcon).attr("data-prefix", "fas");
                        $(likeIcon).attr("data-prefix", "far");
                    } else if($(dislikeIcon).data("prefix") === "fas") {
                        $(dislikeIcon).attr("data-prefix", "far");
                    }
                    $(commentDiv).find(`#likeCount`).text(response.likes);
                    $(commentDiv).find(`#dislikeCount`).text(response.dislikes);
                    return;
                }   
            }
                        
        },
        error: function(xhr, status, error) {
            if(xhr.status === 401) {
                let response = JSON.parse(xhr.responseText);
                window.location.href = response.redirect;
            }
            else{
                console.log(error);
            }
        }
        
    })
}

function handleFollowUnfollowUser(event, userId) {
    const btn = event.currentTarget;
    let POST_URL = window.location.href
    let action = ""
    if (btn.id === "followBtn") {
        POST_URL = `${POST_URL}follow/`
        action = "follow"
    }
    else if(btn.id === "unfollowBtn") {
        POST_URL = `${POST_URL}unfollow/`
        action = "unfollow"
    }
    
    $.ajax({
        url: POST_URL,
        type: "POST",
        headers:{
            'X-CSRFToken': $('input[name=csrfmiddlewaretoken]').val()
        },
        data: {
            user_id: userId,
            action: action
        },
        success: function(response) {
            if(response) {
                if(response?.success){
                    if(btn.id === "followBtn") {
                        $(btn).removeClass("btn-outline-primary").addClass("btn-primary");
                        btn.id = "unfollowBtn";
                        btn.innerText = "Unfollow";
                    }
                    else if(btn.id === "unfollowBtn") {
                        $(btn).removeClass("btn-primary").addClass("btn-outline-primary");
                        btn.id = "followBtn";
                        btn.innerText = "Follow";
                    }
                    return;
                }   
            }                         
        },
        error: function(xhr, status, error) {
            if(xhr.status === 401) {
                let response = JSON.parse(xhr.responseText);
                window.location.href = response.redirect;
            }
            else{
                console.log(error);
            }
        }
        
    })
}

