#!/bin/bash

# AMRAP Calculator Release Script
# Creates a tagged release with proper version management

set -e  # Exit on any error

echo "🚀 AMRAP Calculator Release Script"
echo "=================================="

# Check if we're in a git repository
if ! git rev-parse --git-dir > /dev/null 2>&1; then
    echo "❌ Error: Not in a git repository"
    exit 1
fi

# Check if working directory is clean
if [[ -n $(git status --porcelain) ]]; then
    echo "❌ Error: Working directory is not clean. Please commit or stash changes first."
    git status --short
    exit 1
fi

# Get current branch
CURRENT_BRANCH=$(git branch --show-current)
echo "📍 Current branch: $CURRENT_BRANCH"

# Get the last tag (if any)
LAST_TAG=$(git describe --tags --abbrev=0 2>/dev/null || echo "No previous tags")
echo "🏷️  Last tag: $LAST_TAG"

echo ""
echo "📝 Release Information"
echo "---------------------"

# Prompt for version
while true; do
    read -p "Enter version (e.g., v1.0.0, v0.1.2): " .VERSION
    if [[ $VERSION =~ ^v[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
        break
    else
        echo "❌ Invalid version format. Please use vX.Y.Z (e.g., v1.0.0)"
    fi
done

# Check if tag already exists
if git rev-parse "$VERSION" >/dev/null 2>&1; then
    echo "❌ Error: Tag $VERSION already exists"
    exit 1
fi

# Prompt for release title
read -p "Enter release title: " RELEASE_TITLE

# Prompt for release description
echo "Enter release description (press Ctrl+D when done):"
RELEASE_DESCRIPTION=$(cat)

echo ""
echo "📋 Release Summary"
echo "------------------"
echo "Version: $VERSION"
echo "Title: $RELEASE_TITLE"
echo "Branch: $CURRENT_BRANCH"
echo "Description:"
echo "$RELEASE_DESCRIPTION"

echo ""
read -p "🤔 Proceed with release? (y/N): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "❌ Release cancelled"
    exit 1
fi

echo ""
echo "🔄 Creating release..."

# Update .VERSION file
echo "📝 Updating .VERSION file..."
VERSION_NUM=${VERSION#v}  # Remove 'v' prefix for .VERSION file
echo "$VERSION_NUM" > src/.VERSION
git add src/.VERSION
git commit -m "Bump version to $VERSION"
echo "✅ .VERSION file updated and committed"

# Create the tag with annotation
git tag -a "$VERSION" -m "$RELEASE_TITLE

$RELEASE_DESCRIPTION"

echo "✅ Created tag: $VERSION"

# Push the tag to origin
echo "📤 Pushing tag to origin..."
git push origin "$VERSION"

echo "✅ Tag pushed to origin"

# Push current branch if it has unpushed commits
UNPUSHED=$(git log origin/$CURRENT_BRANCH..$CURRENT_BRANCH --oneline 2>/dev/null || echo "")
if [[ -n $UNPUSHED ]]; then
    echo "📤 Pushing current branch..."
    git push origin "$CURRENT_BRANCH"
    echo "✅ Branch pushed to origin"
fi

echo ""
echo "🎉 Release $VERSION created successfully!"
echo ""
echo "📌 What was done:"
echo "  • Created annotated tag: $VERSION"
echo "  • Pushed tag to origin"
echo "  • Pushed branch: $CURRENT_BRANCH"
echo ""
echo "🔗 Next steps:"
echo "  • Check GitHub releases page to create a GitHub release"
echo "  • Update documentation if needed"
echo "  • Announce the release"
echo ""
echo "📜 Tag details:"
git show "$VERSION" --no-patch --format="Tag: %D%nDate: %ad%nAuthor: %an <%ae>%nMessage: %B"