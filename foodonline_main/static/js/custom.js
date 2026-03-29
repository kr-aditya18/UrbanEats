$(document).ready(function(){

    // ─── INJECT STYLES ──────────────────────────────────────────────────────────
    $('head').append(`<style>
        /* ── Toast ── */
        #food-toast {
            position: fixed;
            top: 16px;
            right: 16px;
            z-index: 99999;
            display: flex;
            align-items: center;
            gap: 12px;
            padding: 14px 18px;
            border-radius: 16px;
            background: #fff;
            box-shadow: 0 10px 40px rgba(0,0,0,0.15);
            width: calc(100vw - 32px);
            max-width: 320px;
            transform: translateX(calc(100% + 32px));
            opacity: 0;
            transition: transform 0.4s cubic-bezier(.34,1.56,.64,1), opacity 0.3s ease;
            font-family: 'Segoe UI', sans-serif;
            box-sizing: border-box;
        }
        #food-toast.show {
            transform: translateX(0);
            opacity: 1;
        }
        #food-toast .toast-icon {
            width: 40px;
            height: 40px;
            min-width: 40px;
            border-radius: 10px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 20px;
        }
        #food-toast .toast-body { flex: 1; min-width: 0; }
        #food-toast .toast-title {
            font-size: 13px;
            font-weight: 700;
            color: #1a1a1a;
            margin: 0 0 2px;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
        }
        #food-toast .toast-sub {
            font-size: 11px;
            color: #888;
            margin: 0;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
        }
        #food-toast .toast-bar {
            position: absolute;
            bottom: 0; left: 0;
            height: 3px;
            border-radius: 0 0 16px 16px;
            width: 100%;
            transform-origin: left;
            animation: shrink 2.2s linear forwards;
        }
        @keyframes shrink {
            from { transform: scaleX(1); }
            to   { transform: scaleX(0); }
        }

        /* ── Overlay ── */
        #food-overlay {
            display: none;
            position: fixed;
            inset: 0;
            background: rgba(0,0,0,0.5);
            backdrop-filter: blur(5px);
            -webkit-backdrop-filter: blur(5px);
            z-index: 99998;
            align-items: flex-end;
            justify-content: center;
            padding: 0;
        }
        #food-overlay.show { display: flex; }

        /* ── Modal ── */
        #food-modal {
            background: #fff;
            border-radius: 24px 24px 0 0;
            width: 100%;
            max-width: 100%;
            overflow: hidden;
            box-shadow: 0 -10px 60px rgba(0,0,0,0.2);
            transform: translateY(100%);
            opacity: 0;
            transition: transform 0.4s cubic-bezier(.34,1.56,.64,1), opacity 0.3s ease;
            font-family: 'Segoe UI', sans-serif;
        }
        #food-modal.show {
            transform: translateY(0);
            opacity: 1;
        }
        #food-modal .modal-handle {
            width: 40px;
            height: 4px;
            background: rgba(255,255,255,0.5);
            border-radius: 2px;
            margin: 12px auto 0;
        }
        #food-modal .modal-banner {
            padding: 20px 24px 24px;
            text-align: center;
        }
        #food-modal .modal-emoji {
            font-size: 56px;
            line-height: 1;
            margin-bottom: 10px;
            display: block;
            filter: drop-shadow(0 4px 12px rgba(0,0,0,0.1));
        }
        #food-modal .modal-title {
            margin: 0 0 4px;
            font-size: 20px;
            font-weight: 700;
            color: #fff;
        }
        #food-modal .modal-sub {
            margin: 0;
            font-size: 13px;
            color: rgba(255,255,255,0.88);
        }
        #food-modal .modal-body {
            padding: 20px 20px 32px;
            text-align: center;
        }
        #food-modal .modal-body p {
            color: #666;
            font-size: 14px;
            margin: 0 0 20px;
            line-height: 1.6;
        }
        #food-modal .modal-actions {
            display: flex;
            flex-direction: column;
            gap: 10px;
        }
        #food-modal .btn-primary-modal {
            width: 100%;
            padding: 15px;
            border: none;
            border-radius: 14px;
            font-size: 15px;
            font-weight: 700;
            cursor: pointer;
            color: #fff;
            transition: transform 0.15s, box-shadow 0.15s;
            letter-spacing: 0.3px;
        }
        #food-modal .btn-primary-modal:active {
            transform: scale(0.97);
        }
        #food-modal .btn-secondary-modal {
            width: 100%;
            padding: 14px;
            border: 1.5px solid #e0e0e0;
            border-radius: 14px;
            font-size: 14px;
            font-weight: 600;
            cursor: pointer;
            background: #fff;
            color: #888;
            transition: background 0.2s;
        }
        #food-modal .btn-secondary-modal:active {
            background: #f5f5f5;
        }

        /* ── Desktop overrides (≥ 540px) ── */
        @media (min-width: 540px) {
            #food-toast {
                top: 24px;
                right: 24px;
                width: 320px;
                transform: translateX(360px);
            }
            #food-overlay {
                align-items: center;
                padding: 24px;
            }
            #food-modal {
                border-radius: 24px;
                max-width: 380px;
                box-shadow: 0 30px 80px rgba(0,0,0,0.25);
                transform: scale(0.8) translateY(40px);
            }
            #food-modal.show {
                transform: scale(1) translateY(0);
            }
            #food-modal .modal-handle { display: none; }
            #food-modal .modal-actions {
                flex-direction: row;
            }
            #food-modal .btn-primary-modal,
            #food-modal .btn-secondary-modal {
                flex: 1;
                width: auto;
            }
            #food-modal .modal-emoji { font-size: 64px; }
            #food-modal .modal-title { font-size: 22px; }
        }
    </style>`);

    // ─── INJECT HTML ────────────────────────────────────────────────────────────
    $('body').append(`
        <div id="food-toast">
            <div class="toast-icon" id="toast-icon-box"></div>
            <div class="toast-body">
                <p class="toast-title" id="toast-title"></p>
                <p class="toast-sub"   id="toast-sub"></p>
            </div>
            <div class="toast-bar" id="toast-bar"></div>
        </div>

        <div id="food-overlay">
            <div id="food-modal">
                <div class="modal-banner" id="modal-banner">
                    <div class="modal-handle"></div>
                    <span class="modal-emoji" id="modal-emoji"></span>
                    <h2 class="modal-title" id="modal-title"></h2>
                    <p  class="modal-sub"   id="modal-sub"></p>
                </div>
                <div class="modal-body">
                    <p id="modal-desc"></p>
                    <div class="modal-actions" id="modal-actions"></div>
                </div>
            </div>
        </div>
    `);

    // ─── TOAST ──────────────────────────────────────────────────────────────────
    let toastTimer;
    function showToast(type, title, sub){
        const configs = {
            success:  { bg: '#e8f8f0', color: '#22c55e', emoji: '✅' },
            removed:  { bg: '#fff4e5', color: '#f97316', emoji: '🗑️' },
            decrease: { bg: '#fef9c3', color: '#eab308', emoji: '➖' },
            error:    { bg: '#fee2e2', color: '#ef4444', emoji: '❌' },
        };
        const c = configs[type] || configs.error;

        $('#toast-icon-box').css('background', c.bg).html(`<span style="font-size:20px">${c.emoji}</span>`);
        $('#toast-title').text(title);
        $('#toast-sub').text(sub || '');
        $('#toast-bar').css('background', c.color).css('animation', 'none');

        // restart animation
        setTimeout(function(){
            $('#toast-bar').css('animation', 'shrink 2.2s linear forwards');
        }, 10);

        const $toast = $('#food-toast');
        $toast.addClass('show');

        clearTimeout(toastTimer);
        toastTimer = setTimeout(function(){
            $toast.removeClass('show');
        }, 2400);
    }

    // ─── MODAL ──────────────────────────────────────────────────────────────────
    function showModal(config){
        $('#modal-banner').css('background', config.bannerBg);
        $('#modal-emoji').text(config.emoji);
        $('#modal-title').text(config.title);
        $('#modal-sub').text(config.sub);
        $('#modal-desc').text(config.desc);

        let html = '';
        if(config.primaryText)
            html += `<button class="btn-primary-modal" id="modal-primary-btn" style="background:${config.primaryColor}">${config.primaryText}</button>`;
        if(config.secondaryText)
            html += `<button class="btn-secondary-modal" id="modal-secondary-btn">${config.secondaryText}</button>`;
        $('#modal-actions').html(html);

        const $overlay = $('#food-overlay');
        const $modal   = $('#food-modal');

        $overlay.addClass('show');
        setTimeout(function(){ $modal.addClass('show'); }, 10);

        $('#modal-primary-btn').off('click').on('click', function(){
            closeModal();
            if(config.onPrimary) config.onPrimary();
        });
        $('#modal-secondary-btn').off('click').on('click', function(){
            closeModal();
        });
        $overlay.off('click').on('click', function(e){
            if($(e.target).is('#food-overlay')) closeModal();
        });
    }

    function closeModal(){
        $('#food-modal').removeClass('show');
        setTimeout(function(){
            $('#food-overlay').removeClass('show');
        }, 380);
    }

    // ─── PRESETS ────────────────────────────────────────────────────────────────
    function handleLoginRequired(){
        showModal({
            bannerBg:     'linear-gradient(135deg, #ff6b35, #f7931e)',
            emoji:        '🍽️',
            title:        'Hungry? Login First!',
            sub:          'Your cart is waiting for you',
            desc:         'You need to be logged in to add delicious items to your cart.',
            primaryText:  '🔑 Login Now',
            primaryColor: '#ff6b35',
            secondaryText:'Maybe Later',
            onPrimary: function(){ window.location.href = '/accounts/login/'; }
        });
    }

    function handleError(msg){
        showModal({
            bannerBg:     'linear-gradient(135deg, #ef4444, #f87171)',
            emoji:        '😕',
            title:        'Oops!',
            sub:          'Something went wrong',
            desc:         msg || 'An unexpected error occurred. Please try again.',
            primaryText:  'Got it',
            primaryColor: '#ef4444',
        });
    }

    function handleNetworkError(){
        showModal({
            bannerBg:     'linear-gradient(135deg, #6366f1, #818cf8)',
            emoji:        '📡',
            title:        'No Connection',
            sub:          'Could not reach the server',
            desc:         'Please check your internet connection and try again.',
            primaryText:  'Retry',
            primaryColor: '#6366f1',
            secondaryText:'Cancel',
        });
    }

    // ─── ADD TO CART ────────────────────────────────────────────────────────────
    $('.add_to_cart').on('click', function(e){
        e.preventDefault();
        let url     = $(this).data("url");
        let food_id = $(this).data("id");

        $.ajax({
            type: 'GET', url: url,
            headers: { 'X-Requested-With': 'XMLHttpRequest' },
            success: function(response){
                if(response.status === 'login_required'){ handleLoginRequired(); return; }
                if(response.status === 'failed'){ handleError(response.message); return; }
                $('#cart_counter').html(response.cart_counter.cart_count);
                $('#qty-' + food_id).text(response.qty);
                showToast('success', 'Added to cart!', 'Item added successfully 🛒');
            },
            error: function(){ handleNetworkError(); }
        });
    });

    // ─── DECREASE CART ──────────────────────────────────────────────────────────
    $('.decrease_cart').on('click', function(e){
        e.preventDefault();
        let url     = $(this).data("url");
        let food_id = $(this).data("id");

        $.ajax({
            type: 'GET', url: url,
            headers: { 'X-Requested-With': 'XMLHttpRequest' },
            success: function(response){
                if(response.status === 'login_required'){ handleLoginRequired(); return; }
                if(response.status === 'failed'){ handleError(response.message); return; }
                $('#cart_counter').html(response.cart_counter.cart_count);
                $('#qty-' + food_id).text(response.qty);
                if(response.qty === 0){
                    showToast('removed', 'Item removed!', 'Removed from your cart 🗑️');
                } else {
                    showToast('decrease', 'Quantity decreased', 'Now ' + response.qty + ' in cart');
                }
            },
            error: function(){ handleNetworkError(); }
        });
    });

});