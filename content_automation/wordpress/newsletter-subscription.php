<?php
/**
 * Plugin Name: Betania Newsletter Subscription
 * Plugin URI: https://betania.io
 * Description: Simple newsletter subscription form for Betania Tech Newsletter
 * Version: 1.0.0
 * Author: Betania
 * License: GPL2
 */

// Prevent direct access
if (!defined('ABSPATH')) {
    exit;
}

/**
 * Add subscriber to database
 */
function betania_add_subscriber($email, $name = '') {
    global $wpdb;
    $table_name = $wpdb->prefix . 'newsletter_subscribers';

    // Generate tokens
    $confirmation_token = bin2hex(random_bytes(32));
    $unsubscribe_token = bin2hex(random_bytes(32));

    // Insert or update subscriber
    $existing = $wpdb->get_row($wpdb->prepare(
        "SELECT * FROM $table_name WHERE email = %s",
        $email
    ));

    if ($existing) {
        // Update existing subscriber
        $wpdb->update(
            $table_name,
            array(
                'name' => $name,
                'active' => true
            ),
            array('email' => $email)
        );
        return array(
            'success' => true,
            'message' => 'Subscription updated!',
            'confirmation_token' => $existing->confirmation_token
        );
    } else {
        // Insert new subscriber
        $result = $wpdb->insert(
            $table_name,
            array(
                'email' => $email,
                'name' => $name,
                'subscribed_at' => current_time('mysql'),
                'confirmed' => false,
                'confirmation_token' => $confirmation_token,
                'unsubscribe_token' => $unsubscribe_token,
                'active' => true
            ),
            array('%s', '%s', '%s', '%d', '%s', '%s', '%d')
        );

        if ($result) {
            // TODO: Send confirmation email via Python service
            // For now, we'll auto-confirm for testing
            // You can integrate with your Python email service here

            return array(
                'success' => true,
                'message' => 'Successfully subscribed! Please check your email to confirm.',
                'confirmation_token' => $confirmation_token
            );
        } else {
            return array(
                'success' => false,
                'message' => 'Subscription failed. Please try again.'
            );
        }
    }
}

/**
 * Handle AJAX subscription
 */
function betania_handle_subscription() {
    // Verify nonce
    check_ajax_referer('betania_newsletter_nonce', 'nonce');

    $email = sanitize_email($_POST['email']);
    $name = sanitize_text_field($_POST['name']);

    // Validate email
    if (!is_email($email)) {
        wp_send_json_error(array('message' => 'Invalid email address.'));
    }

    // Add subscriber
    $result = betania_add_subscriber($email, $name);

    if ($result['success']) {
        wp_send_json_success($result);
    } else {
        wp_send_json_error($result);
    }
}
add_action('wp_ajax_betania_subscribe', 'betania_handle_subscription');
add_action('wp_ajax_nopriv_betania_subscribe', 'betania_handle_subscription');

/**
 * Subscription form shortcode
 * Usage: [betania_newsletter_form]
 */
function betania_newsletter_form_shortcode($atts) {
    $atts = shortcode_atts(array(
        'title' => 'Subscribe to Our Newsletter',
        'description' => 'Get the top 5 software engineering news every week!',
        'button_text' => 'Subscribe'
    ), $atts);

    ob_start();
    ?>
    <div class="betania-newsletter-form" id="betania-newsletter-form">
        <style>
            .betania-newsletter-form {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                padding: 40px;
                border-radius: 10px;
                color: white;
                max-width: 600px;
                margin: 20px auto;
                box-shadow: 0 10px 30px rgba(0,0,0,0.1);
            }
            .betania-newsletter-form h3 {
                margin: 0 0 10px 0;
                color: white;
                font-size: 24px;
            }
            .betania-newsletter-form p {
                margin: 0 0 20px 0;
                opacity: 0.9;
            }
            .betania-newsletter-form input[type="text"],
            .betania-newsletter-form input[type="email"] {
                width: 100%;
                padding: 12px;
                margin-bottom: 10px;
                border: none;
                border-radius: 5px;
                font-size: 16px;
                box-sizing: border-box;
            }
            .betania-newsletter-form button {
                background: white;
                color: #667eea;
                border: none;
                padding: 12px 30px;
                border-radius: 5px;
                font-size: 16px;
                font-weight: bold;
                cursor: pointer;
                width: 100%;
                transition: transform 0.2s;
            }
            .betania-newsletter-form button:hover {
                transform: scale(1.05);
            }
            .betania-newsletter-form button:disabled {
                opacity: 0.6;
                cursor: not-allowed;
            }
            .betania-newsletter-message {
                margin-top: 15px;
                padding: 10px;
                border-radius: 5px;
                text-align: center;
            }
            .betania-newsletter-message.success {
                background: rgba(255, 255, 255, 0.2);
            }
            .betania-newsletter-message.error {
                background: rgba(255, 0, 0, 0.2);
            }
        </style>

        <h3><?php echo esc_html($atts['title']); ?></h3>
        <p><?php echo esc_html($atts['description']); ?></p>

        <form id="betania-subscribe-form">
            <input
                type="text"
                name="name"
                id="betania-name"
                placeholder="Your Name (optional)"
                autocomplete="name"
            />
            <input
                type="email"
                name="email"
                id="betania-email"
                placeholder="Your Email Address"
                required
                autocomplete="email"
            />
            <button type="submit" id="betania-submit">
                <?php echo esc_html($atts['button_text']); ?>
            </button>
        </form>

        <div id="betania-message" class="betania-newsletter-message" style="display: none;"></div>
    </div>

    <script>
    (function() {
        const form = document.getElementById('betania-subscribe-form');
        const message = document.getElementById('betania-message');
        const submitBtn = document.getElementById('betania-submit');

        form.addEventListener('submit', function(e) {
            e.preventDefault();

            const email = document.getElementById('betania-email').value;
            const name = document.getElementById('betania-name').value;

            // Disable button
            submitBtn.disabled = true;
            submitBtn.textContent = 'Subscribing...';
            message.style.display = 'none';

            // Send AJAX request
            fetch('<?php echo admin_url('admin-ajax.php'); ?>', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                },
                body: new URLSearchParams({
                    action: 'betania_subscribe',
                    email: email,
                    name: name,
                    nonce: '<?php echo wp_create_nonce('betania_newsletter_nonce'); ?>'
                })
            })
            .then(response => response.json())
            .then(data => {
                message.style.display = 'block';

                if (data.success) {
                    message.className = 'betania-newsletter-message success';
                    message.textContent = data.data.message;
                    form.reset();
                } else {
                    message.className = 'betania-newsletter-message error';
                    message.textContent = data.data.message || 'Subscription failed. Please try again.';
                }
            })
            .catch(error => {
                message.style.display = 'block';
                message.className = 'betania-newsletter-message error';
                message.textContent = 'An error occurred. Please try again.';
            })
            .finally(() => {
                submitBtn.disabled = false;
                submitBtn.textContent = '<?php echo esc_js($atts['button_text']); ?>';
            });
        });
    })();
    </script>
    <?php
    return ob_get_clean();
}
add_shortcode('betania_newsletter_form', 'betania_newsletter_form_shortcode');

/**
 * Handle confirmation
 */
function betania_handle_confirmation() {
    if (isset($_GET['confirm_newsletter']) && isset($_GET['token'])) {
        global $wpdb;
        $table_name = $wpdb->prefix . 'newsletter_subscribers';
        $token = sanitize_text_field($_GET['token']);

        $result = $wpdb->update(
            $table_name,
            array('confirmed' => true),
            array('confirmation_token' => $token),
            array('%d'),
            array('%s')
        );

        if ($result) {
            echo '<div style="text-align: center; padding: 50px;">
                <h2>✅ Subscription Confirmed!</h2>
                <p>Thank you for subscribing to Betania Tech Newsletter. You will receive the top 5 software engineering news every week.</p>
            </div>';
            exit;
        }
    }
}
add_action('template_redirect', 'betania_handle_confirmation');

/**
 * Handle unsubscribe
 */
function betania_handle_unsubscribe() {
    if (isset($_GET['unsubscribe']) && isset($_GET['token'])) {
        global $wpdb;
        $table_name = $wpdb->prefix . 'newsletter_subscribers';
        $token = sanitize_text_field($_GET['token']);

        $result = $wpdb->update(
            $table_name,
            array('active' => false),
            array('unsubscribe_token' => $token),
            array('%d'),
            array('%s')
        );

        if ($result) {
            echo '<div style="text-align: center; padding: 50px;">
                <h2>Unsubscribed</h2>
                <p>You have been successfully unsubscribed from Betania Tech Newsletter.</p>
            </div>';
            exit;
        }
    }
}
add_action('template_redirect', 'betania_handle_unsubscribe');
?>
