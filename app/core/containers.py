from functools import lru_cache

import punq

from app.services.auth import AbstractAuthService, AuthService
from app.services.cart_items import AbstractCartItemService, CartItemService
from app.services.carts import AbstractCartService, CartService
from app.services.categories import AbstractCategoryService, CategoryService
from app.services.files import AbstractFileUploadService, FileUploadService
from app.services.messages import AbstractMessageService, MessageService
from app.services.product_images import AbstractProductImageService, ProductImageService
from app.services.products import AbstractProductService, ProductService
from app.services.tokens import AbstractJWTTokenService, JWTTokenService
from app.services.users import AbstractUserService, UserService
from app.use_cases.auth.login import LoginUserUseCase
from app.use_cases.auth.refresh import RefreshTokenUseCase
from app.use_cases.auth.registration import RegisterUserUseCase
from app.use_cases.cart.change_items_quantity import AbstractChangeItemQuantityUseCase, ChangeItemQuantityUseCase
from app.use_cases.cart.create import AbstractCreateCartUseCase, CreateCartUseCase
from app.use_cases.cart.create_cart_item import AbstractAddToCartUseCase, AddToCartUseCase
from app.use_cases.cart.delete_item import AbstractDeleteFromCartUseCase, DeleteFromCartUseCase
from app.use_cases.cart.fetch import AbstractFetchCartUseCase, FetchCartUseCase
from app.use_cases.cart.merge import AbstractMergeCartsUseCase, MergeCartsUseCase
from app.use_cases.categories.create import AbstractCreateCategoryUseCase, CreateCategoryUseCase
from app.use_cases.categories.delete import AbstractDeleteCategoryUseCase, DeleteCategoryUseCase
from app.use_cases.categories.fetch_all import AbstractFetchCategoriesUseCase, FetchCategoriesUseCase
from app.use_cases.categories.update import AbstractUpdateCategoryUseCase, UpdateCategoryUseCase
from app.use_cases.messages.create_messages import AbstractCreateMessageUseCase, CreateMessageUseCase
from app.use_cases.messages.fetch_message import AbstractFetchMessageUseCase, FetchMessageUseCase
from app.use_cases.messages.fetch_messages import AbstractFetchMessagesUseCase, FetchMessagesUseCase
from app.use_cases.products.create import AbstractCreateProductUseCase, CreateProductUseCase
from app.use_cases.products.fetch_all import AbstractFetchProductsUseCase, FetchProductsUseCase
from app.use_cases.products.fetch_one import AbstractFetchProductUseCase, FetchProductUseCase
from app.use_cases.users.update import AbstractUpdateUserUseCase, UpdateUserUseCase


@lru_cache(1)
def get_container() -> punq.Container:
    return _initialize_container()


def _initialize_container() -> punq.Container:
    container = punq.Container()

    # Services
    container.register(AbstractAuthService, AuthService)
    container.register(AbstractUserService, UserService)
    container.register(AbstractJWTTokenService, JWTTokenService)
    container.register(AbstractMessageService, MessageService)
    container.register(AbstractCategoryService, CategoryService)
    container.register(AbstractProductService, ProductService)
    container.register(AbstractProductImageService, ProductImageService)
    container.register(AbstractFileUploadService, FileUploadService)
    container.register(AbstractCartService, CartService)
    container.register(AbstractCartItemService, CartItemService)

    # Use cases
    container.register(RegisterUserUseCase)
    container.register(LoginUserUseCase)
    container.register(RefreshTokenUseCase)
    container.register(AbstractCreateMessageUseCase, CreateMessageUseCase)
    container.register(AbstractFetchMessagesUseCase, FetchMessagesUseCase)
    container.register(AbstractFetchMessageUseCase, FetchMessageUseCase)
    container.register(AbstractFetchCategoriesUseCase, FetchCategoriesUseCase)
    container.register(AbstractCreateCategoryUseCase, CreateCategoryUseCase)
    container.register(AbstractUpdateCategoryUseCase, UpdateCategoryUseCase)
    container.register(AbstractDeleteCategoryUseCase, DeleteCategoryUseCase)
    container.register(AbstractFetchProductsUseCase, FetchProductsUseCase)
    container.register(AbstractFetchProductUseCase, FetchProductUseCase)
    container.register(AbstractCreateProductUseCase, CreateProductUseCase)
    container.register(AbstractFetchCartUseCase, FetchCartUseCase)
    container.register(AbstractCreateCartUseCase, CreateCartUseCase)
    container.register(AbstractMergeCartsUseCase, MergeCartsUseCase)
    container.register(AbstractAddToCartUseCase, AddToCartUseCase)
    container.register(AbstractDeleteFromCartUseCase, DeleteFromCartUseCase)
    container.register(AbstractChangeItemQuantityUseCase, ChangeItemQuantityUseCase)
    container.register(AbstractUpdateUserUseCase, UpdateUserUseCase)

    return container
