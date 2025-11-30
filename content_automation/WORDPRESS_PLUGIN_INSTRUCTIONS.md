# WordPress Plugin Installation Guide

## Installing the Newsletter Subscription Plugin

### Method 1: Via WordPress Admin (Recommended)

1. **Prepare the Plugin File**
   ```bash
   cd wordpress
   zip -r betania-newsletter-subscription.zip newsletter-subscription.php
   ```

2. **Upload to WordPress**
   - Go to your WordPress admin: `https://betania.io/wp-admin`
   - Navigate to: Plugins → Add New → Upload Plugin
   - Click "Choose File" and select `betania-newsletter-subscription.zip`
   - Click "Install Now"
   - Click "Activate Plugin"

### Method 2: Via FTP/SFTP

1. **Connect to Your Server**
   ```bash
   # Using scp
   scp newsletter-subscription.php your-user@betania.io:/path/to/wordpress/wp-content/plugins/

   # Or use an FTP client like FileZilla
   ```

2. **Activate in WordPress**
   - Go to: Plugins → Installed Plugins
   - Find "Betania Newsletter Subscription"
   - Click "Activate"

### Method 3: Via SSH

```bash
# SSH into your server
ssh your-user@betania.io

# Navigate to plugins directory
cd /path/to/wordpress/wp-content/plugins/

# Create plugin directory
mkdir betania-newsletter
cd betania-newsletter

# Upload the file (use your preferred method)
nano newsletter-subscription.php  # Then paste the content

# Or download from your repo
wget https://raw.githubusercontent.com/your-repo/path/newsletter-subscription.php

# Set permissions
chmod 644 newsletter-subscription.php

# Activate via WP-CLI (if installed)
wp plugin activate betania-newsletter-subscription
```

## Adding the Subscription Form to Your Website

### Option 1: Using Shortcode (Easiest)

1. Create a new page or edit existing one
2. Add this shortcode anywhere:
   ```
   [betania_newsletter_form]
   ```

3. Customize (optional):
   ```
   [betania_newsletter_form
       title="Join Our Tech Community"
       description="Get weekly insights delivered to your inbox"
       button_text="Sign Me Up!"]
   ```

### Option 2: In Theme Template

Edit your theme files (e.g., `sidebar.php` or `footer.php`):

```php
<?php
if (shortcode_exists('betania_newsletter_form')) {
    echo do_shortcode('[betania_newsletter_form]');
}
?>
```

### Option 3: Using Widget (Classic Editor)

1. Go to: Appearance → Widgets
2. Add "Custom HTML" widget
3. Insert:
   ```html
   [betania_newsletter_form]
   ```

### Option 4: Using Block Editor

1. Edit any page/post
2. Add a "Shortcode" block
3. Enter: `[betania_newsletter_form]`

## Customizing the Form Appearance

### Via Shortcode Parameters

```
[betania_newsletter_form
    title="Your Custom Title"
    description="Your custom description"
    button_text="Subscribe Now"]
```

### Via Custom CSS

Add to: Appearance → Customize → Additional CSS

```css
/* Change gradient colors */
.betania-newsletter-form {
    background: linear-gradient(135deg, #your-color-1 0%, #your-color-2 100%);
}

/* Change button color */
.betania-newsletter-form button {
    background: #your-color !important;
    color: white !important;
}

/* Change form width */
.betania-newsletter-form {
    max-width: 800px;  /* Default is 600px */
}
```

### Advanced: Edit Plugin File

If you want permanent changes, edit `newsletter-subscription.php` directly:

```php
// Find this section around line 150
<style>
    .betania-newsletter-form {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        /* Change these colors */
    }
</style>
```

## Testing the Plugin

### 1. Test the Form

1. Visit the page with the subscription form
2. Enter a test email
3. Submit
4. You should see: "Successfully subscribed! Please check your email to confirm."

### 2. Verify Database Entry

```sql
-- Connect to your WordPress database
SELECT * FROM wp_newsletter_subscribers
ORDER BY subscribed_at DESC
LIMIT 5;
```

You should see your test email with:
- `confirmed = 0` (not confirmed yet)
- `active = 1` (active)
- A `confirmation_token`
- An `unsubscribe_token`

### 3. Test Confirmation Link

The confirmation URL format is:
```
https://betania.io/?confirm_newsletter=1&token=YOUR_TOKEN
```

Get the token from database and visit this URL. You should see:
```
✅ Subscription Confirmed!
Thank you for subscribing...
```

### 4. Test Unsubscribe

The unsubscribe URL format is:
```
https://betania.io/?unsubscribe=1&token=YOUR_UNSUBSCRIBE_TOKEN
```

## Connecting to Python Email Service

### Option 1: Webhook (Recommended)

Add this to the plugin (after line 88 in `newsletter-subscription.php`):

```php
// Send webhook to Python service for confirmation email
$webhook_url = 'https://your-azure-function.azurewebsites.net/api/send_confirmation';
wp_remote_post($webhook_url, array(
    'body' => json_encode(array(
        'email' => $email,
        'name' => $name,
        'confirmation_token' => $confirmation_token
    )),
    'headers' => array('Content-Type' => 'application/json')
));
```

### Option 2: Direct PHP Email (Temporary)

The plugin will auto-confirm subscribers for now. Later, integrate with your Python email service via webhook or cron job.

## Troubleshooting

### Plugin Not Showing Up

**Problem**: Plugin doesn't appear in Plugins list

**Solution**:
1. Check file permissions: `chmod 644 newsletter-subscription.php`
2. Verify file location: `/wp-content/plugins/newsletter-subscription.php`
3. Check for PHP errors: Enable WP_DEBUG in wp-config.php

### Form Not Appearing

**Problem**: Shortcode shows as text

**Solution**:
1. Make sure plugin is activated
2. Check if you're using the correct shortcode: `[betania_newsletter_form]`
3. Clear cache (if using caching plugin)

### AJAX Not Working

**Problem**: Form submits but nothing happens

**Solution**:
1. Check browser console for errors (F12)
2. Verify AJAX URL is correct
3. Check nonce verification
4. Disable conflicting plugins

### Database Errors

**Problem**: "Table doesn't exist"

**Solution**:
```sql
-- Manually create table
CREATE TABLE wp_newsletter_subscribers (
    -- See full schema in plugin file or README_SETUP.md
);
```

## Next Steps

After installing the plugin:

1. ✅ Test subscription flow
2. ✅ Customize form appearance
3. ✅ Add form to prominent location (sidebar, footer, dedicated page)
4. ✅ Set up confirmation email integration
5. ✅ Test with Python automation system

## Support

Issues? Check:
- Plugin file syntax (no PHP errors)
- WordPress version compatibility (5.0+)
- Database table created
- Proper file permissions

For more help, see main [README_SETUP.md](README_SETUP.md)
